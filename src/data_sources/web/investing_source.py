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
    
    def _load_local_cache(self, symbol: str) -> tuple[pd.Series | None, bool]:
        """Load historical data from local file."""
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
            
            is_validated = symbol_data.get('_validated', False)
            data_dict = {k: v for k, v in symbol_data.items() if not k.startswith('_')}
            series = pd.Series({pd.to_datetime(k): v['value'] for k, v in data_dict.items()}).sort_index()
            
            print(f"[INVESTING][CACHE] Loaded {len(series)} records for {symbol}, latest: {series.index[-1].date()}, validated: {is_validated}")
            return series, is_validated
        except Exception as e:
            print(f"[INVESTING][CACHE] Error loading cache: {e}")
            return None, False
    
    def _save_to_local_cache(self, symbol: str, data: pd.Series, is_validated: bool = False):
        """Save historical data to local file with validation flag."""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self._cache_file.exists():
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        symbol_data = {
            d.strftime('%Y-%m-%d'): {'value': float(v), 'timestamp': datetime.now().isoformat()}
            for d, v in data.items()
        }
        symbol_data['_validated'] = is_validated
        all_data[symbol] = symbol_data
        
        with open(self._cache_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"[INVESTING][CACHE] Saved {len(data)} records for {symbol}, validated={is_validated}")
    
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
    
    async def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
        """Fetch market breadth data with local file caching and validation."""
        if symbol not in self.SYMBOL_URLS:
            raise ValueError(f"Unsupported symbol: {symbol}. Available: {list(self.SYMBOL_URLS.keys())}")
        
        url = self.SYMBOL_URLS[symbol]
        ma_period = self.SYMBOL_MA_PERIOD[symbol]
        
        return self._fetch_with_cache_and_scrape(
            symbol=symbol,
            period=period,
            load_cache_fn=lambda: self._load_local_cache(symbol),
            save_cache_fn=lambda data, is_validated: self._save_to_local_cache(symbol, data, is_validated),
            scrape_fn=lambda: self._scrape_data(url),
            build_result_fn=lambda period_data, merged: {
                'data': period_data,
                'symbol': symbol,
                'ma_period': ma_period,
                'current': float(merged.iloc[-1])
            }
        )
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Create market breadth chart."""
        series_data = data['data']
        ma_period = data['ma_period']
        
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

