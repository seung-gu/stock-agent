"""
Unified data source system for financial indicators.

Supports automatic source detection and data fetching from:
- yfinance (stocks, ETFs, treasuries)
- FRED (economic indicators)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional
import re
import os

import yfinance as yf
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
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch data from yfinance."""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            raise ValueError(f"No data found for {symbol} with period {period}")
        
        return {
            'history': hist,
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
        """Convert period string to timedelta."""
        period_map = {
            '5d': timedelta(days=7),  # Get extra for weekends
            '1mo': timedelta(days=35),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730)
        }
        return period_map.get(period, timedelta(days=180))
    
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
        
        latest = float(series_data.iloc[-1])
        latest_date = series_data.index[-1].strftime('%Y-%m-%d')
        
        # Get changes over different periods
        one_week_ago = float(series_data.iloc[-5]) if len(series_data) >= 5 else None
        one_month_ago = float(series_data.iloc[-20]) if len(series_data) >= 20 else None
        
        result = {
            'period': period,
            'latest': latest,
            'latest_date': latest_date,
        }
        
        if one_week_ago is not None:
            result['change_1w'] = latest - one_week_ago
        
        if one_month_ago is not None:
            result['change_1m'] = latest - one_month_ago
        
        return result


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

