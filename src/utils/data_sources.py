"""
Unified data source system for financial indicators.

Supports automatic source detection and data fetching from:
- yfinance (stocks, ETFs, treasuries)
- FRED (economic indicators)
- investing.com (market breadth indicators via direct API)
"""

import os
import json
import pandas as pd
import yfinance as yf
import requests
import finnhub
from pathlib import Path
from bs4 import BeautifulSoup
from pandas.tseries.offsets import BDay
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from fredapi import Fred
from dotenv import load_dotenv

from src.utils.charts import create_yfinance_chart, create_fred_chart, create_line_chart
from src.utils.technical_indicators import calculate_sma

# Load environment variables
load_dotenv()


class DataSource(ABC):
    """Base class for all data sources."""
    # Shared cache across all instances of the same subclass
    _cache: dict[str, Any] = {}
    
    def __init__(self):
        """Initialize data source (cache is class-level)."""
        pass
    
    @staticmethod
    def _get_period_rank(period: str) -> int:
        """Get period rank for comparison (higher = longer)."""
        period_ranks = {
            '5d': 1, '1mo': 2, '3mo': 3, '6mo': 4, 
            '1y': 5, '2y': 6, '5y': 7, '10y': 8, 'max': 9
        }
        return period_ranks.get(period.lower(), 5)  # Default to 1y
    
    def _should_fetch(self, symbol: str, period: str) -> bool:
        """Determine if we need to fetch data from API."""
        cached = self._cache.get(symbol)
        if not cached:
            return True
        if self._get_period_rank(period) > self._get_period_rank(cached['period']):
            return True
        return False
    
    @abstractmethod
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """
        Fetch raw data from the source.
        
        Args:
            symbol: Symbol or indicator code
            period: Time period (5d, 1mo, 6mo, etc.)
            
        Returns:
            Dictionary with data and metadata
        """
        pass
    
    @abstractmethod
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """
        Create chart from fetched data.
        
        Args:
            data: Data returned from fetch_data()
            symbol: Symbol or indicator code
            period: Time period
            label: Human-readable label for chart title (optional)
            
        Returns:
            Chart information string with path
        """
        pass
    
    @abstractmethod
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """
        Extract analysis metadata from data.
        
        Args:
            data: Data returned from fetch_data()
            period: Time period
            
        Returns:
            Dictionary with analysis metrics
        """
        pass
    
    def get_actual_period_approx(self, data: dict[str, Any]) -> str:
        """
        Find closest matching period by comparing actual days with standard periods.
        
        Args:
            data: Data returned from fetch_data()
            
        Returns:
            Approximated period string (e.g., '1y', '6mo')
        """
        data_with_index = data['data']
        
        # Remove NaN values to get actual valid data range
        if hasattr(data_with_index, 'dropna'):
            data_with_index = data_with_index.dropna()
        
        if len(data_with_index) == 0:
            return "5d"  # Default fallback
        
        actual_days = (data_with_index.index[-1] - data_with_index.index[0]).days
        
        # Try all standard periods and find closest match
        periods = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"]
        
        best_match = periods[0]
        min_diff = float('inf')
        
        for period in periods:
            expected_days = self._period_to_timedelta(period).days
            diff = abs(actual_days - expected_days)
            if diff < min_diff:
                min_diff = diff
                best_match = period

        return best_match


class YFinanceSource(DataSource):
    """Data source for stocks, ETFs, and treasuries via yfinance."""
    
    def __init__(self):
        """Initialize with smart cache for API optimization."""
        super().__init__()  # Initialize cache from base class
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert yfinance period string to approximate timedelta for display window."""
        period_map = {
            '5d': timedelta(days=7),      # ~5 trading days with weekends
            '1mo': timedelta(days=30),    # ~22 trading days with weekends
            '3mo': timedelta(days=90),   # ~65 trading days with weekends
            '6mo': timedelta(days=182),   # ~130 trading days with weekends
            '1y': timedelta(days=365),    # ~252 trading days with weekends
            '2y': timedelta(days=730),    # ~504 trading days with weekends
            '5y': timedelta(days=1825),   # ~1260 trading days with weekends
            '10y': timedelta(days=3650),  # ~2520 trading days with weekends
            'max': timedelta(days=36500),  # ~100 years for max
        }
        period_lower = period.lower()
        if period_lower not in period_map:
            print(f"Warning: Unsupported period '{period}', using default 6mo (200 days)")
            return timedelta(days=200)  # Default: 6mo equivalent
        return period_map[period_lower]
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch data from yfinance with intelligent caching."""
        period_lower = (period or '').lower()
        cached = self._cache.get(symbol)
        if not period_lower:
            # Default empty period to cached period if available, else sensible default
            if cached and cached.get('period'):
                print(f"[YF][WARN] Empty period for {symbol}; defaulting to cached period '{cached['period']}'")
                period_lower = cached['period']
            else:
                print(f"[YF][WARN] Empty period for {symbol}; defaulting to '1y'")
                period_lower = '1y'
        
        
        if self._should_fetch(symbol, period_lower):
            print(f"[YF][API] Fetching data: symbol={symbol}, period={period_lower}")
            # Fetch data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            
            if period_lower == 'max':
                hist = ticker.history(period='max')
            else:
                display_delta = self._period_to_timedelta(period_lower)
                start_display = end_date - display_delta
                
                # Determine buffer by trading days using BusinessDay offset with safety margin for holidays
                max_window = 20 if period_lower in ['1mo', '3mo'] else 200
                safety_margin = 20  # extra trading days to cover holiday gaps
                fetch_start = pd.Timestamp(start_display.date()) - BDay(max_window + safety_margin)
                hist = ticker.history(start=fetch_start, end=end_date)
            
            if hist.empty:
                raise ValueError(f"No data found for {symbol} with period {period_lower}")
            
            # Normalize timezone
            try:
                hist.index = hist.index.tz_localize(None)
            except (TypeError, AttributeError):
                pass
            
            # Get info (only once per symbol)
            info = {}
            if cached and 'info' in cached:
                info = cached['info']
            else:
                try:
                    info = getattr(ticker, 'info', {}) or {}
                except Exception:
                    info = {}
            
            # Update cache with longest data
            self._cache[symbol] = {
                'hist': hist,
                'info': info,
                'period': period_lower,
                'fetched_at': datetime.now()
            }
            cached = self._cache[symbol]
        else:
            if cached:
                print(f"[YF][CACHE] Using cached data: symbol={symbol}, cached_period={cached['period']} → requested={period_lower}")
        
        # Get cached data
        hist = cached['hist']
        info = cached['info']
        
        # Compute SMA columns ONCE on the full cached history if missing
        if 'Close' in hist.columns:
            if 'SMA_5' not in hist.columns:
                hist['SMA_5'] = calculate_sma(hist, 5)
            if 'SMA_20' not in hist.columns:
                hist['SMA_20'] = calculate_sma(hist, 20)
            if 'SMA_200' not in hist.columns:
                hist['SMA_200'] = calculate_sma(hist, 200)

        # Slice to requested period (align to first available trading day >= start_display)
        if period_lower == 'max':
            hist_display = hist
        else:
            end_date = datetime.now()
            display_delta = self._period_to_timedelta(period_lower)
            start_display = (end_date - display_delta).date()
            start_display_ts = pd.Timestamp(start_display)
            # ensure SMA_200 is valid from the first row of the display slice
            first_valid_ts = None
            if 'SMA_200' in hist.columns:
                first_valid_ts = hist['SMA_200'].first_valid_index()
            effective_start = start_display_ts
            if first_valid_ts is not None and first_valid_ts > effective_start:
                effective_start = first_valid_ts
            pos = hist.index.searchsorted(effective_start)
            hist_display = hist.iloc[pos:]

        return {
            'data': hist_display,
            'info': info,
            'symbol': symbol
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Create stock/treasury chart."""
        hist = data['data']
        info = data['info']
        
        # Determine chart configuration
        chart_config = self._get_chart_config(symbol, info)
        
        return create_yfinance_chart(
            data=hist,
            period=period,
            ylabel=chart_config['ylabel'],
            value_format=chart_config['value_format'],
            label=label or symbol
        )
    
    def _get_chart_config(self, symbol: str, info: dict) -> dict:
        """Get chart configuration for yfinance data."""
        ticker_name = info.get('longName', symbol)
        quote_type = info.get('quoteType', 'EQUITY')
        currency = info.get('currency', 'USD')
        
        if any(keyword in ticker_name.upper() for keyword in ['TREASURY', 'YIELD', 'INTEREST']):
            return {
                'ylabel': 'Yield (%)',
                'value_format': '{:.3f}%'
            }
        elif quote_type == 'INDEX':
            return {
                'ylabel': 'Index Value',
                'value_format': '{:.2f}'
            }
        else:
            return {
                'ylabel': f'Price ({currency})',
                'value_format': f'{currency} {{}}'
            }
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract basic analysis metrics from yfinance data (without technical indicators)."""
        hist = data['data']
        
        start_price = float(hist['Close'].iloc[0])
        end_price = float(hist['Close'].iloc[-1])
        change_pct = ((end_price - start_price) / start_price) * 100
        
        return {
            'period': period,
            'start': start_price,
            'end': end_price,
            'change_pct': change_pct,
            'high': float(hist['Close'].max()),
            'low': float(hist['Close'].min()),
            'volatility': float(hist['Close'].pct_change().std() * (len(hist) ** 0.5) * 100)
        }


class FREDSource(DataSource):
    """Data source for economic indicators via FRED API."""
    
    def __init__(self):
        # Lazy initialization - only create Fred client when needed
        super().__init__()  # Initialize cache from base class
        self._fred = None
        
        # Indicator-specific configurations
        self.indicator_configs = {
            'NFCI': {
                'name': 'National Financial Conditions Index',
                'baseline': 0,
                'positive_label': 'Tighter Conditions',
                'negative_label': 'Looser Conditions'
            },
            'DFF': {
                'name': 'Federal Funds Effective Rate',
                'baseline': None,
                'positive_label': 'Above Target',
                'negative_label': 'Below Target'
            },
            'T10Y2Y': {
                'name': '10-Year Treasury Minus 2-Year',
                'baseline': 0,
                'positive_label': 'Positive Spread',
                'negative_label': 'Inverted Yield Curve'
            }
        }
    
    @property
    def fred(self):
        """Lazy initialization of FRED client."""
        if self._fred is None:
            self._fred = Fred(api_key=os.getenv('FRED_API_KEY'))
        return self._fred
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert period string to timedelta for FRED data (weekly frequency)."""
        period_map = {
            '5d': timedelta(days=7),      # ~1 week for weekly data
            '1mo': timedelta(days=30),    # ~4 weeks for weekly data
            '3mo': timedelta(days=90),    # ~13 weeks for weekly data
            '6mo': timedelta(days=180),   # ~26 weeks for weekly data
            '1y': timedelta(days=365),    # ~52 weeks for weekly data
            '2y': timedelta(days=730),    # ~104 weeks for weekly data
            '5y': timedelta(days=1825),   # ~260 weeks for weekly data
            '10y': timedelta(days=3650),  # ~520 weeks for weekly data
            'max': timedelta(days=36500),  # ~100 years for max
        }
        period_lower = period.lower()
        if period_lower not in period_map:
            print(f"Warning: Unsupported period '{period}', using default 6mo (180 days)")
            return timedelta(days=180)  # Default: 6mo equivalent
        return period_map[period_lower]
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch data from FRED API with intelligent caching."""
        period_lower = (period or '').lower()
        cached = self._cache.get(symbol)
        if not period_lower:
            # Default empty period to cached period if available, else sensible default
            if cached and cached.get('period'):
                print(f"[FRED][WARN] Empty period for {symbol}; defaulting to cached period '{cached['period']}'")
                period_lower = cached['period']
            else:
                print(f"[FRED][WARN] Empty period for {symbol}; defaulting to '6mo'")
                period_lower = '6mo'
        
        
        if self._should_fetch(symbol, period_lower):
            print(f"[FRED][API] Fetching data: symbol={symbol}, period={period_lower}")
            # Fetch data
            end_date = datetime.now()
            start_date = end_date - self._period_to_timedelta(period_lower)
            
            series_data = self.fred.get_series(
                symbol,
                observation_start=start_date.strftime('%Y-%m-%d'),
                observation_end=end_date.strftime('%Y-%m-%d')
            )
            
            if series_data.empty:
                raise ValueError(f"No FRED data found for {symbol} with period {period_lower}")
            
            # Update cache with longest data
            self._cache[symbol] = {
                'data': series_data,
                'period': period_lower,
                'fetched_at': datetime.now()
            }
            cached = self._cache[symbol]
        else:
            if cached:
                print(f"[FRED][CACHE] Using cached data: symbol={symbol}, cached_period={cached['period']} → requested={period_lower}")
        
        # Get cached data
        series_data = cached['data']
        
        # Slice to requested period
        if period_lower == cached['period']:
            period_data = series_data
        else:
            end_date = datetime.now()
            start_date = end_date - self._period_to_timedelta(period_lower)
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Filter data to requested period
            period_data = series_data[(series_data.index >= start_date_str) & (series_data.index <= end_date_str)]
            
            if period_data.empty:
                # If no data in period, use the most recent data
                period_data = series_data.tail(1)
        
        config = self.indicator_configs.get(symbol, {
            'name': symbol,
            'baseline': None,
            'positive_label': 'Above Baseline',
            'negative_label': 'Below Baseline'
        })
        
        return {
            'data': period_data,
            'symbol': symbol,
            'config': config
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Create FRED indicator chart."""
        series_data = data['data']
        config = data['config']
        
        return create_fred_chart(
            data=series_data,
            label=label or config['name'],
            period=period,
            baseline=config.get('baseline'),
            positive_label=config.get('positive_label', 'Above Baseline'),
            negative_label=config.get('negative_label', 'Below Baseline')
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from FRED data."""
        series_data = data['data']
        
        # Get start and end values for the period
        start_value = float(series_data.iloc[0])
        end_value = float(series_data.iloc[-1])
        change_pct = ((end_value - start_value) / start_value) * 100
        
        return {
            'period': period,
            'start': start_value,
            'end': end_value,
            'change_pct': change_pct,
            'high': float(series_data.max()),
            'low': float(series_data.min()),
            'volatility': float(series_data.pct_change().std() * (len(series_data) ** 0.5) * 100)
        }


class InvestingSource(DataSource):
    """Data source for market breadth indicators via Investing.com scraping."""
    
    # Symbol to URL mapping
    SYMBOL_URLS = {
        'S5TH': 'https://www.investing.com/indices/sp-500-stocks-above-200-day-average',
        'S5FI': 'https://www.investing.com/indices/s-p-500-stocks-above-50-day-average',
    }
    
    # Symbol to MA period mapping
    SYMBOL_MA_PERIOD = {
        'S5TH': 200,
        'S5FI': 50,
    }
    
    def __init__(self):
        """Initialize with file-based cache."""
        super().__init__()
        self._cache_file = Path('data/market_breadth_history.json')
    
    def _load_local_cache(self, symbol: str) -> tuple[pd.Series | None, bool]:
        """Load historical data from local file.
        
        Returns:
            (data, is_validated): data series and validation flag
        """
        if not self._cache_file.exists():
            print(f"[INVESTING][CACHE] Cache file not found: {self._cache_file}")
            return None, False
        try:
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
            
            symbol_data = all_data.get(symbol, {})
            if not symbol_data:
                print(f"[INVESTING][CACHE] No data for symbol {symbol} in cache")
                return None, False
            
            # Check validation flag
            is_validated = symbol_data.get('_validated', False)
            
            # Extract data (skip metadata keys starting with _)
            data_dict = {k: v for k, v in symbol_data.items() if not k.startswith('_')}
            series = pd.Series({pd.to_datetime(k): v['value'] for k, v in data_dict.items()}).sort_index()
            
            print(f"[INVESTING][CACHE] Loaded {len(series)} records for {symbol}, latest: {series.index[-1].date()}, validated: {is_validated}")
            return series, is_validated
        except Exception as e:
            print(f"[INVESTING][CACHE] Error loading cache: {e}")
            return None, False
    
    def _save_to_local_cache(self, symbol: str, data: pd.Series, is_validated: bool = False):
        """Save historical data to local file with validation flag.
        
        Args:
            symbol: Symbol to save
            data: Data series
            is_validated: True if data has been validated (complete up to latest scraped date)
        """
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        if self._cache_file.exists():
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        # Update symbol data
        symbol_data = {
            d.strftime('%Y-%m-%d'): {'value': float(v), 'timestamp': datetime.now().isoformat()}
            for d, v in data.items()
        }
        
        # Add validation flag
        symbol_data['_validated'] = is_validated
        
        all_data[symbol] = symbol_data
        
        # Save to file
        with open(self._cache_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"[INVESTING][CACHE] Saved {len(data)} records for {symbol}, validated={is_validated}")
    
    def _scrape_data(self, url: str) -> pd.Series:
        """Scrape market breadth from Investing.com historical data table."""
        response = requests.get(f"{url}-historical-data", headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }, timeout=15)
        response.raise_for_status()
        table = BeautifulSoup(response.text, 'html.parser').find('table')
        if not table:
            raise ValueError("No data table found")
        data = [(pd.to_datetime(row.find_all('td')[0].get_text(strip=True), format='%b %d, %Y'),
                 float(row.find_all('td')[1].get_text(strip=True).replace(',', '')))
                for row in table.find_all('tr')[1:] if len(row.find_all('td')) >= 2]
        return pd.Series(dict(data)).sort_index()
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert period string to timedelta."""
        period_map = {
            '5d': timedelta(days=7),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=182),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825),
            '10y': timedelta(days=3650),
            'max': timedelta(days=36500),  # ~100 years for max
        }
        period_lower = (period or '1y').lower()
        return period_map.get(period_lower, timedelta(days=365))
    
    async def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
        """Fetch market breadth data with local file caching and validation."""
        if symbol not in self.SYMBOL_URLS:
            raise ValueError(f"Unsupported symbol: {symbol}. Available: {list(self.SYMBOL_URLS.keys())}")
        
        url = self.SYMBOL_URLS[symbol]
        ma_period = self.SYMBOL_MA_PERIOD[symbol]
        period = period or '1y'
        
        print(f"[INVESTING][FETCH] symbol={symbol}, period={period}")
        
        # Load local cache with validation flag
        local, is_validated = self._load_local_cache(symbol)
        
        # Always scrape first to check latest available date
        print(f"[INVESTING][SCRAPE] Fetching from {url}")
        scraped = self._scrape_data(url)
        latest_scraped_date = scraped.index[-1].date()
        print(f"[INVESTING][SCRAPE] Scraped {len(scraped)} records, range: {scraped.index[0].date()} to {latest_scraped_date}")
        
        # Determine if we need to update cache
        need_update = True
        
        if local is not None and len(local) > 0:
            latest_cached_date = local.index[-1].date()
            
            if is_validated and latest_cached_date >= latest_scraped_date:
                # validated + cache has all scraped data → no update needed
                print(f"[INVESTING][CACHE] Validated and up-to-date (cached: {latest_cached_date}, scraped: {latest_scraped_date}), using cache")
                need_update = False
                merged = local
            elif is_validated and latest_cached_date < latest_scraped_date:
                # validated + new data available → update needed
                print(f"[INVESTING][CACHE] Validated but outdated (cached: {latest_cached_date}, scraped: {latest_scraped_date}), will update")
            else:
                # not validated → update needed (fill missing dates)
                print(f"[INVESTING][CACHE] Not validated, will update and validate")
        else:
            print(f"[INVESTING][CACHE] No local cache found, will create")
        
        # Update cache if needed
        if need_update:
            if local is not None:
                # Merge: keep all local data + add new scraped data
                merged = pd.concat([local, scraped]).sort_index()
                # Remove duplicates, keeping the scraped value (more recent)
                merged = merged[~merged.index.duplicated(keep='last')]
                
                missing_dates = scraped.index.difference(local.index)
                if len(missing_dates) > 0:
                    print(f"[INVESTING][MERGE] Added {len(missing_dates)} missing dates")
                print(f"[INVESTING][MERGE] Total after merge: {len(merged)} records")
            else:
                merged = scraped
            
            # Save with validation flag (validated)
            self._save_to_local_cache(symbol, merged, is_validated=True)
        
        # Slice to requested period
        end_date = datetime.now()
        start_date = end_date - self._period_to_timedelta(period)
        period_data = merged[merged.index >= start_date]
        
        print(f"[INVESTING][RETURN] Returning {len(period_data)} records for period {period}")
        
        return {
            'data': period_data if len(period_data) > 0 else merged,
            'symbol': symbol,
            'ma_period': ma_period,
            'current': float(merged.iloc[-1])
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Create market breadth chart."""
        series_data = data['data']
        ma_period = data['ma_period']
        
        # Convert Series to DataFrame for create_line_chart
        df = series_data.to_frame(name='Breadth')
        
        return create_line_chart(
            data=df,
            label=label or f"S&P 500 Stocks Above {ma_period}-Day MA",
            period=period or '1y',
            ylabel='Percentage (%)',
            data_column='Breadth',
            threshold_upper=70.0,
            threshold_lower=30.0,
            overbought_label='Strong Breadth',
            oversold_label='Weak Breadth'
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from market breadth data."""
        series_data = data['data']
        
        start_value = float(series_data.iloc[0])
        end_value = float(series_data.iloc[-1])
        change_pct = end_value - start_value  # Absolute change for percentage data
        
        return {
            'period': period or '1y',
            'start': start_value,
            'end': end_value,
            'change': change_pct,
            'high': float(series_data.max()),
            'low': float(series_data.min()),
            'ma_period': data['ma_period']
        }


class FinnhubSource(DataSource):
    """Data source for company fundamentals via Finnhub API."""
    
    def __init__(self):
        """Initialize with lazy API client."""
        super().__init__()
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of Finnhub client."""
        if self._client is None:
            api_key = os.getenv('FINNHUB_API_KEY')
            if not api_key:
                raise ValueError("FINNHUB_API_KEY not found in environment variables")
            self._client = finnhub.Client(api_key=api_key)
        return self._client
    
    async def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
        """
        Fetch Forward P/E data from Finnhub (quote + EPS estimates).
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Not used for fundamentals (included for interface compatibility)
            
        Returns:
            Dictionary with current price and forward EPS
        """
        try:
            # Get current quote
            quote = self.client.quote(symbol)
            current_price = quote.get('c') if quote else None
            
            if not current_price:
                return {
                    'symbol': symbol,
                    'current_price': None,
                    'forward_eps_ntm': None,
                    'error': 'Failed to fetch current price'
                }
            
            # Get Forward EPS (NTM): Last actual quarter + Next 3 estimated quarters
            forward_eps_ntm = None
            try:
                # Get past earnings (actuals)
                past_earnings = self.client.company_earnings(symbol, limit=1)
                last_actual = past_earnings[0].get('actual', 0) if past_earnings else 0
                
                # Get future estimates
                from_date = datetime.now().strftime('%Y-%m-%d')
                to_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
                
                earnings_cal = self.client.earnings_calendar(
                    _from=from_date,
                    to=to_date,
                    symbol=symbol,
                    international=False
                )
                
                estimates = earnings_cal.get('earningsCalendar', [])
                next_3_estimates = sum(e.get('epsEstimate', 0) for e in estimates[:3])
                
                # NTM = Last actual Q + Next 3 estimated Q
                forward_eps_ntm = last_actual + next_3_estimates
                
            except Exception as e:
                print(f"[FINNHUB] Could not fetch forward estimates: {e}")
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'forward_eps_ntm': forward_eps_ntm,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[FINNHUB] Error fetching data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'current_price': None,
                'forward_eps_ntm': None,
                'error': str(e)
            }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Not implemented for fundamentals data."""
        return f"Chart generation not supported for Finnhub fundamentals data"
    
    def get_analysis(self, data: dict[str, Any], period: str = None) -> dict[str, Any]:
        """
        Calculate Forward P/E (NTM) from fetched data.
        
        Returns:
            Dictionary with Forward P/E ratio
        """
        current_price = data.get('current_price')
        forward_eps_ntm = data.get('forward_eps_ntm')
        forward_pe_ntm = None
        
        if current_price and forward_eps_ntm and forward_eps_ntm > 0:
            forward_pe_ntm = current_price / forward_eps_ntm
        
        return {
            'symbol': data.get('symbol'),
            'current_price': current_price,
            'forward_eps_ntm': forward_eps_ntm,
            'forward_pe_ntm': forward_pe_ntm
        }


def get_data_source(source: str) -> DataSource:
    """Get data source by name."""
    sources = {
        'yfinance': YFinanceSource,
        'yf': YFinanceSource,
        'fred': FREDSource,
        'investing': InvestingSource,
        'inv': InvestingSource,
        'finnhub': FinnhubSource,
        'fh': FinnhubSource
    }
    source_lower = source.lower()
    if source_lower not in sources:
        raise ValueError(f"Unknown source: {source}. Available: {list(sources.keys())}")
    return sources[source_lower]()
