"""
Unified data source system for financial indicators.

Supports automatic source detection and data fetching from:
- yfinance (stocks, ETFs, treasuries)
- FRED (economic indicators)
"""

import os
import pandas as pd
import yfinance as yf
from pandas.tseries.offsets import BDay
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from fredapi import Fred
from dotenv import load_dotenv

from src.utils.charts import create_yfinance_chart, create_fred_chart
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
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str) -> str:
        """
        Create chart from fetched data.
        
        Args:
            data: Data returned from fetch_data()
            symbol: Symbol or indicator code
            period: Time period
            
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
            'history': hist_display,
            'info': info,
            'symbol': symbol
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str) -> str:
        """Create stock/treasury chart."""
        hist = data['history']
        info = data['info']
        
        # Determine chart configuration
        chart_config = self._get_chart_config(symbol, info)
        
        return create_yfinance_chart(
            ticker=symbol,
            data=hist,
            period=period,
            ylabel=chart_config['ylabel'],
            value_format=chart_config['value_format']
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
        hist = data['history']
        
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
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str) -> str:
        """Create FRED indicator chart."""
        series_data = data['data']
        config = data['config']
        
        return create_fred_chart(
            data=series_data,
            indicator_name=config['name'],
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


def get_data_source(source: str) -> DataSource:
    """
    Get data source by explicit name.
    
    Args:
        source: Data source name ("yfinance" or "fred")
        
    Returns:
        DataSource instance
        
    Raises:
        ValueError: If source name is not recognized
    """
    sources = {
        'yfinance': YFinanceSource,
        'yf': YFinanceSource,
        'fred': FREDSource,
    }
    
    source_lower = source.lower()
    if source_lower not in sources:
        raise ValueError(f"Unknown source: {source}. Available: {list(sources.keys())}")
    
    # Return a new instance; cache is class-level and shared across instances
    return sources[source_lower]()

