"""
Unified data source system for financial indicators.

Supports automatic source detection and data fetching from:
- yfinance (stocks, ETFs, treasuries)
- FRED (economic indicators)
"""

import os
import pandas as pd
import yfinance as yf
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from fredapi import Fred
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Charts will be imported when needed to avoid circular imports


class DataSource(ABC):
    """Base class for all data sources."""
    
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
    async def create_chart(self, data: dict[str, str | int | float | dict], symbol: str, period: str) -> str:
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
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert yfinance period string to approximate timedelta for display window."""
        period_map = {
            '5d': timedelta(days=7),      # ~5 trading days with weekends
            '1mo': timedelta(days=35),    # ~22 trading days with weekends
            '3mo': timedelta(days=100),   # ~65 trading days with weekends
            '6mo': timedelta(days=200),   # ~130 trading days with weekends
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
        """Fetch data from yfinance."""
        ticker = yf.Ticker(symbol)
        period_lower = (period or '').lower()
        
        # Determine if we need extra lookback for SMA 200
        needs_sma_200 = period_lower in ['1y', '2y', '5y', '10y', 'max']
        end_date = datetime.now()
        display_delta = self._period_to_timedelta(period_lower)
        start_display = end_date - display_delta
        
        if period_lower == 'max':
            hist = ticker.history(period='max')
        else:
            # Fetch with buffer if 200-SMA needed (approx 280 calendar days ~ 200 trading days)
            fetch_start = start_display - (timedelta(days=280) if needs_sma_200 else timedelta(days=0))
            hist = ticker.history(start=fetch_start, end=end_date)
        
        if hist.empty:
            raise ValueError(f"No data found for {symbol} with period {period}")
        
        # Normalize timezone for safe datetime comparisons
        try:
            hist.index = hist.index.tz_localize(None)
        except (TypeError, AttributeError):
            pass

        # Compute common SMAs for convenience (5/20/200)
        try:
            if 'Close' in hist.columns:
                from src.utils.technical_indicators import calculate_sma
                
                if 'SMA_5' not in hist.columns:
                    hist['SMA_5'] = calculate_sma(hist, window=5)
                if 'SMA_20' not in hist.columns:
                    hist['SMA_20'] = calculate_sma(hist, window=20)
                if 'SMA_200' not in hist.columns:
                    hist['SMA_200'] = calculate_sma(hist, window=200)
        except Exception:
            # If SMA computation fails, continue without SMAs
            pass
        
        # Slice back to display window so chart reflects requested period
        if period_lower != 'max':
            # Ensure start_display is pandas Timestamp and naive
            start_display_ts = pd.Timestamp(start_display).tz_localize(None)
            hist_display = hist[hist.index >= start_display_ts]
        else:
            hist_display = hist
        
        return {
            'history': hist_display,
            'info': ticker.info,
            'symbol': symbol
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str) -> str:
        """Create stock/treasury chart."""
        hist = data['history']
        info = data['info']
        
        # Determine chart configuration
        chart_config = self._get_chart_config(symbol, info)
        
        from src.utils.charts import create_yfinance_chart
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
        """Extract analysis metrics from yfinance data."""
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
            'volatility': float(hist['Close'].std())
        }


class FREDSource(DataSource):
    """Data source for economic indicators via FRED API."""
    
    def __init__(self):
        # Lazy initialization - only create Fred client when needed
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
        """Fetch data from FRED API."""
        end_date = datetime.now()
        start_date = end_date - self._period_to_timedelta(period)
        
        series_data = self.fred.get_series(
            symbol,
            observation_start=start_date.strftime('%Y-%m-%d'),
            observation_end=end_date.strftime('%Y-%m-%d')
        )
        
        if series_data.empty:
            raise ValueError(f"No FRED data found for {symbol}")
        
        config = self.indicator_configs.get(symbol, {
            'name': symbol,
            'baseline': None,
            'positive_label': 'Above Baseline',
            'negative_label': 'Below Baseline'
        })
        
        return {
            'data': series_data,
            'symbol': symbol,
            'config': config
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str) -> str:
        """Create FRED indicator chart."""
        series_data = data['data']
        config = data['config']
        
        from src.utils.charts import create_chart
        return create_chart(
            data=series_data,
            title=config['name'],
            ylabel=f'{config["name"]} Value',
            period=period,
            value_format='{:.3f}',
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
            'volatility': float(series_data.std())
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
    
    return sources[source_lower]()

