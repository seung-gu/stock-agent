"""YCharts data source for CBOE Put/Call Ratio."""

import json
import pandas as pd
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Any

from src.data_sources.base import WebDataSource
from src.utils.charts import create_line_chart


class YChartsSource(WebDataSource):
    """Data source for CBOE Put/Call Ratio via YCharts scraping."""
    
    SYMBOL_URLS = {
        'CBOE_PUT_CALL_EQUITY': 'https://ycharts.com/indicators/cboe_equity_put_call_ratio',
    }
    
    def __init__(self):
        super().__init__()
        self._cache_file = Path('data/put_call_ratio_history.json')
    
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
        period_lower = period.lower()
        if period_lower not in period_map:
            return timedelta(days=90)  # Default: 3mo
        return period_map[period_lower]
    
    
    def _scrape_data(self, url: str) -> pd.Series:
        """Scrape Put-Call Ratio from YCharts."""
        response = requests.get(url, headers=self.BROWSER_HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        
        if not tables:
            raise ValueError("No data table found on YCharts")
        
        data = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    date_text = cells[0].get_text(strip=True)
                    value_text = cells[1].get_text(strip=True)
                    
                    try:
                        # Try to parse as date and value
                        date_obj = pd.to_datetime(date_text)
                        value = float(value_text)
                        data.append((date_obj, value))
                    except (ValueError, TypeError):
                        # Not a valid date-value pair, skip
                        continue
        
        if not data:
            raise ValueError("No valid data scraped from YCharts")
        
        series = pd.Series(dict(data)).sort_index()
        print(f"[YCHARTS][SCRAPE] Scraped {len(series)} records, range: {series.index[0].date()} to {series.index[-1].date()}")
        return series
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch Put-Call Ratio data with local file caching and web scraping."""
        if symbol not in self.SYMBOL_URLS:
            raise ValueError(f"YChartsSource only supports: {list(self.SYMBOL_URLS.keys())}, got: {symbol}")
        
        url = self.SYMBOL_URLS[symbol]
        
        return self._fetch_with_cache_and_scrape(
            symbol=symbol,
            period=period,
            load_cache_fn=lambda: self._load_local_cache(symbol, 'YCHARTS'),
            save_cache_fn=lambda data, is_validated: self._save_local_cache(symbol, data, is_validated, 'YCHARTS'),
            scrape_fn=lambda: self._scrape_data(url),
            build_result_fn=lambda period_data, merged: {
                'data': period_data,
                'symbol': symbol,
                'current': float(merged.iloc[-1])
            },
            date_offset_tolerance=0
        )
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'line', **kwargs) -> str:
        """Create Put-Call Ratio chart.
        
        Args:
            chart_type: 'line' (default and only option for web sources)
            **kwargs: All parameters for create_line_chart (ylabel, threshold_upper, threshold_lower, etc.)
        """
        series_data = data['data']
        
        return create_line_chart(
            data=series_data,
            label=label or symbol,
            period=period,
            **kwargs
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from Put-Call Ratio data."""
        series_data = data['data']
        
        start_value = float(series_data.iloc[0])
        end_value = float(series_data.iloc[-1])
        change = end_value - start_value
        
        return {
            'period': period,
            'start': start_value,
            'end': end_value,
            'change': change,
            'high': float(series_data.max()),
            'low': float(series_data.min()),
            'mean': float(series_data.mean())
        }

