"""Investing.com data source for market breadth indicators."""

import json
import pandas as pd
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Any

from src.data_sources.base import WebDataSource
from src.utils.charts import create_line_chart


class InvestingSource(WebDataSource):
    """Data source for market breadth indicators via Investing.com scraping."""
    
    SYMBOL_URLS = {
        'S5TH': 'https://www.investing.com/indices/sp-500-stocks-above-200-day-average',
        'S5FI': 'https://www.investing.com/indices/s-p-500-stocks-above-50-day-average',
    }
    
    SYMBOL_MA_PERIOD = {
        'S5TH': 200,
        'S5FI': 50,
    }
    
    def __init__(self):
        super().__init__()
        self._cache_file = Path('data/market_breadth_history.json')
    
    
    def _scrape_data(self, url: str) -> pd.Series:
        """Scrape market breadth from Investing.com historical data table."""
        response = requests.get(f"{url}-historical-data", headers=self.BROWSER_HEADERS, timeout=15)
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
            'max': timedelta(days=36500),
        }
        period_lower = (period or '1y').lower()
        return period_map.get(period_lower, timedelta(days=365))
    
    def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
        """Fetch market breadth data with local file caching and validation."""
        if symbol not in self.SYMBOL_URLS:
            raise ValueError(f"Unsupported symbol: {symbol}. Available: {list(self.SYMBOL_URLS.keys())}")
        
        url = self.SYMBOL_URLS[symbol]
        ma_period = self.SYMBOL_MA_PERIOD[symbol]
        
        return self._fetch_with_cache_and_scrape(
            symbol=symbol,
            period=period,
            load_cache_fn=lambda: self._load_local_cache(symbol, 'INVESTING'),
            save_cache_fn=lambda data, is_validated: self._save_local_cache(symbol, data, is_validated, 'INVESTING'),
            scrape_fn=lambda: self._scrape_data(url),
            build_result_fn=lambda period_data, merged: {
                'data': period_data,
                'symbol': symbol,
                'ma_period': ma_period,
                'current': float(merged.iloc[-1])
            },
            date_offset_tolerance=0
        )
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'line', **kwargs) -> str:
        """Create market breadth chart.
        
        Args:
            chart_type: 'line' (default and only option for web sources)
            **kwargs: All parameters for create_line_chart (ylabel, threshold_upper, threshold_lower, data_column, etc.)
        """
        series_data = data['data']
        
        df = series_data.to_frame(name='Breadth')
        
        return create_line_chart(
            data=df,
            label=label or symbol,
            period=period or '1y',
            **kwargs
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from market breadth data."""
        series_data = data['data']
        
        start_value = float(series_data.iloc[0])
        end_value = float(series_data.iloc[-1])
        change_pct = end_value - start_value
        
        return {
            'period': period or '1y',
            'start': start_value,
            'end': end_value,
            'change': change_pct,
            'high': float(series_data.max()),
            'low': float(series_data.min()),
            'ma_period': data['ma_period']
        }

