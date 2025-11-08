"""FINRA data source for margin statistics."""

import pandas as pd
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import timedelta
from typing import Any

from src.data_sources.base import WebDataSource
from src.utils.charts import create_line_chart


class FINRASource(WebDataSource):
    """Data source for FINRA Margin Statistics."""
    
    # Symbol configuration: column_index, label, cache_file, calculate_yoy
    SYMBOL_CONFIG = {
        'MARGIN_DEBT_YOY': {
            'column_index': 1,
            'label': 'Margin Debt (YoY %)',
            'cache_file': 'margin_debt_history.json',
            'yoy': True
        }
        # Additional symbols can be added here:
    }
    
    def __init__(self):
        super().__init__()
        self._cache_file = None
        self._current_symbol = None
    
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
        return period_map.get(period.lower(), timedelta(days=365))
    
    def _get_symbol_config(self, symbol: str) -> dict:
        """Get configuration for a symbol."""
        if symbol not in self.SYMBOL_CONFIG:
            available = ', '.join(self.SYMBOL_CONFIG.keys())
            raise ValueError(f"Unsupported symbol: {symbol}. Available: {available}")
        return self.SYMBOL_CONFIG[symbol]
    
    def _scrape_data(self, symbol: str) -> pd.Series:
        """Scrape FINRA margin statistics from website for specified symbol."""
        config = self._get_symbol_config(symbol)
        
        url = 'https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics'
        response = requests.get(url, headers=self.BROWSER_HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            raise ValueError("No data table found on FINRA website")
        
        data = []
        
        for row in table.find_all('tr')[1:]:  # Skip header
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            try:
                date_str = cells[0].get_text(strip=True)
                date_obj = pd.to_datetime(date_str, format='%b-%y')
                date_obj = date_obj + pd.offsets.MonthEnd(0)
                
                value_str = cells[config['column_index']].get_text(strip=True).replace(',', '')
                value = float(value_str)
                
                data.append((date_obj, value))
            except Exception as e:
                print(f"[FINRA][SCRAPE] Error parsing row: {e}")
                continue
        
        if not data:
            raise ValueError(f"No valid data scraped from FINRA website for {symbol}")
        
        series = pd.Series(dict(data)).sort_index()
        
        # Calculate YoY if configured
        if config['yoy']:
            series = series.pct_change(periods=12) * 100
        
        print(f"[FINRA][SCRAPE] Scraped {len(series)} records for {symbol}, range: {series.index[0].date()} to {series.index[-1].date()}")
        return series
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch FINRA margin statistics with local file caching.
        
        Args:
            symbol: One of MARGIN_DEBT, MARGIN_DEBT_YOY, FREE_CREDIT_CASH, FREE_CREDIT_MARGIN
            period: Time period (e.g., '1y', '5y', 'max')
        """
        config = self._get_symbol_config(symbol)
        self._cache_file = Path('data') / config['cache_file']
        self._current_symbol = symbol
        
        return self._fetch_with_cache_and_scrape(
            symbol=symbol,
            period=period,
            load_cache_fn=lambda: self._load_local_cache(symbol, 'FINRA'),
            save_cache_fn=lambda data, is_validated: self._save_local_cache(symbol, data, is_validated, 'FINRA'),
            scrape_fn=lambda: self._scrape_data(symbol),
            build_result_fn=lambda period_data, merged: {
                'data': period_data,
                'symbol': symbol,
                'label': config['label'],
                'current': float(merged.iloc[-1]) if len(merged) > 0 else None
            },
            date_offset_tolerance=0
        )
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'line', **kwargs) -> str:
        """Create FINRA margin statistics chart.
        
        Args:
            chart_type: 'line' (default and only option for web sources)
            **kwargs: All parameters for create_line_chart
        """
        series_data = data['data']
        default_label = data.get('label', symbol)
        
        return create_line_chart(
            data=series_data,
            label=label or default_label,
            period=period,
            **kwargs
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from FINRA margin statistics data."""
        series_data = data['data']
        
        if len(series_data) == 0:
            return {
                'period': period,
                'start': None,
                'end': None,
                'change': None,
                'high': None,
                'low': None,
                'mean': None
            }
        
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
