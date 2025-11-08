"""
Unified data source system for financial indicators.

Supports automatic source detection and data fetching from:
- yfinance (stocks, ETFs, treasuries)
- FRED (economic indicators)
- Finnhub (company fundamentals)
- Investing.com (market breadth indicators)
- AAII (investor sentiment)
"""

from src.data_sources.base import DataSource, APIDataSource, WebDataSource
from src.data_sources.api import YFinanceSource, FREDSource, FinnhubSource
from src.data_sources.web import InvestingSource, AAIISource, YChartsSource


def get_data_source(source: str) -> DataSource:
    """Get data source by name."""
    sources = {
        'yfinance': YFinanceSource,
        'yf': YFinanceSource,
        'fred': FREDSource,
        'investing': InvestingSource,
        'inv': InvestingSource,
        'finnhub': FinnhubSource,
        'fh': FinnhubSource,
        'aaii': AAIISource,
        'ycharts': YChartsSource,
        'yc': YChartsSource
    }
    source_lower = source.lower()
    if source_lower not in sources:
        raise ValueError(f"Unknown source: {source}. Available: {list(sources.keys())}")
    return sources[source_lower]()


__all__ = [
    'DataSource',
    'APIDataSource',
    'WebDataSource',
    'YFinanceSource',
    'FREDSource',
    'FinnhubSource',
    'InvestingSource',
    'AAIISource',
    'YChartsSource',
    'get_data_source'
]

