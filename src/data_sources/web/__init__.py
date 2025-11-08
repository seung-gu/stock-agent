"""Web scraping-based data sources."""

from src.data_sources.web.investing_source import InvestingSource
from src.data_sources.web.aaii_source import AAIISource
from src.data_sources.web.ycharts_source import YChartsSource

__all__ = ['InvestingSource', 'AAIISource', 'YChartsSource']

