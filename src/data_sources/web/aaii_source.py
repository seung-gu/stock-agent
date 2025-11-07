"""AAII data source for investor sentiment survey."""

import json
import pandas as pd
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Any

from src.data_sources.base import WebDataSource
from src.utils.charts import create_line_chart


class AAIISource(WebDataSource):
    """Data source for AAII Investor Sentiment Survey (Bull-Bear Spread)."""
    
    def __init__(self):
        super().__init__()
        self._cache_file = Path('data/aaii_bull_bear_spread_history.json')
    
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
            return timedelta(days=365)
        return period_map[period_lower]
    
    def _load_local_cache(self) -> tuple[pd.Series | None, bool]:
        """Load historical data from local file."""
        if not self._cache_file.exists():
            print(f"[AAII][CACHE] Cache file not found: {self._cache_file}")
            return None, False
        try:
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
            
            bull_bear_spread_data = all_data.get('AAII_BULL_BEAR_SPREAD', [])
            if not bull_bear_spread_data:
                print(f"[AAII][CACHE] No sentiment data in cache")
                return None, False
            
            is_validated = all_data.get('_validated', False)
            data_dict = {pd.to_datetime(item['date']): item['value'] for item in bull_bear_spread_data}
            series = pd.Series(data_dict).sort_index()
            
            print(f"[AAII][CACHE] Loaded {len(series)} records, latest: {series.index[-1].date()}, validated: {is_validated}")
            return series, is_validated
        except Exception as e:
            print(f"[AAII][CACHE] Error loading cache: {e}")
            return None, False
    
    def _save_to_local_cache(self, data: pd.Series, is_validated: bool = False):
        """Save historical data to local file with validation flag."""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        bull_bear_spread_data = [
            {'date': d.strftime('%Y-%m-%d'), 'value': float(v)}
            for d, v in data.items()
        ]
        
        all_data = {
            'AAII_BULL_BEAR_SPREAD': bull_bear_spread_data,
            '_validated': is_validated
        }
        
        with open(self._cache_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"[AAII][CACHE] Saved {len(bull_bear_spread_data)} records, validated: {is_validated}")
    
    def _scrape_data(self) -> pd.Series:
        """Scrape latest AAII sentiment data from website."""
        url = 'https://www.aaii.com/sentimentsurvey/sent_results'
        response = requests.get(url, headers=self.BROWSER_HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            raise ValueError("No data table found on AAII website")
        
        data = []
        current_year = datetime.now().year
        
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) < 4:
                continue
            
            try:
                date_str = cells[0].get_text(strip=True)
                date_obj = pd.to_datetime(f"{date_str}, {current_year}", format='%b %d, %Y')
                
                if date_obj > datetime.now():
                    date_obj = pd.to_datetime(f"{date_str}, {current_year - 1}", format='%b %d, %Y')
                
                bullish = float(cells[1].get_text(strip=True).replace('%', '')) / 100
                bearish = float(cells[3].get_text(strip=True).replace('%', '')) / 100
                bull_bear_spread = bullish - bearish
                
                data.append((date_obj, bull_bear_spread))
            except Exception as e:
                print(f"[AAII][SCRAPE] Error parsing row: {e}")
                continue
        
        if not data:
            raise ValueError("No valid data scraped from AAII website")
        
        series = pd.Series(dict(data)).sort_index()
        print(f"[AAII][SCRAPE] Scraped {len(series)} records, range: {series.index[0].date()} to {series.index[-1].date()}")
        return series
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch AAII sentiment data with local file caching and web scraping."""
        if symbol != 'AAII_BULL_BEAR_SPREAD':
            raise ValueError(f"AAIISource only supports 'AAII_BULL_BEAR_SPREAD', got: {symbol}")
        
        return self._fetch_with_cache_and_scrape(
            symbol=symbol,
            period=period,
            load_cache_fn=lambda: self._load_local_cache(),
            save_cache_fn=lambda data, is_validated: self._save_to_local_cache(data, is_validated),
            scrape_fn=lambda: self._scrape_data(),
            build_result_fn=lambda period_data, merged: {
                'data': period_data,
                'symbol': symbol,
                'current': float(merged.iloc[-1])
            },
            date_offset_tolerance=2
        )
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """Create AAII sentiment chart."""
        series_data = data['data']
        
        return create_line_chart(
            data=series_data,
            label=label or 'AAII Bull-Bear Spread',
            ylabel='Bull-Bear Spread',
            period=period,
            threshold_upper=None,
            threshold_lower=-0.2
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from AAII sentiment data."""
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

