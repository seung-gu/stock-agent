"""FRED data source for economic indicators."""

import os
from datetime import datetime, timedelta
from typing import Any
from fredapi import Fred
from dotenv import load_dotenv

from src.data_sources.base import APIDataSource
from src.utils.charts import create_fred_chart

load_dotenv()


class FREDSource(APIDataSource):
    """Data source for economic indicators via FRED API."""
    
    _cache: dict[str, Any] = {}
    
    def __init__(self):
        super().__init__()
        self._fred = None
        
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
        """Convert period string to timedelta for FRED data."""
        period_map = {
            '5d': timedelta(days=7),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825),
            '10y': timedelta(days=3650),
            'max': timedelta(days=36500),
        }
        period_lower = period.lower()
        if period_lower not in period_map:
            print(f"Warning: Unsupported period '{period}', using default 6mo (180 days)")
            return timedelta(days=180)
        return period_map[period_lower]
    
    def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch data from FRED API with intelligent caching."""
        period_lower = (period or '').lower()
        cached = self._cache.get(symbol)
        if not period_lower:
            if cached and cached.get('period'):
                print(f"[FRED][WARN] Empty period for {symbol}; defaulting to cached period '{cached['period']}'")
                period_lower = cached['period']
            else:
                print(f"[FRED][WARN] Empty period for {symbol}; defaulting to '6mo'")
                period_lower = '6mo'
        
        if self._should_fetch(symbol, period_lower):
            print(f"[FRED][API] Fetching data: symbol={symbol}, period={period_lower}")
            end_date = datetime.now()
            start_date = end_date - self._period_to_timedelta(period_lower)
            
            series_data = self.fred.get_series(
                symbol,
                observation_start=start_date.strftime('%Y-%m-%d'),
                observation_end=end_date.strftime('%Y-%m-%d')
            )
            
            if series_data.empty:
                raise ValueError(f"No FRED data found for {symbol} with period {period_lower}")
            
            self._cache[symbol] = {
                'data': series_data,
                'period': period_lower,
                'fetched_at': datetime.now()
            }
            cached = self._cache[symbol]
        else:
            if cached:
                print(f"[FRED][CACHE] Using cached data: symbol={symbol}, cached_period={cached['period']} → requested={period_lower}")
        
        series_data = cached['data']
        
        # Slice to requested period
        if period_lower == cached['period']:
            period_data = series_data
        else:
            end_date = datetime.now()
            start_date = end_date - self._period_to_timedelta(period_lower)
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            period_data = series_data[(series_data.index >= start_date_str) & (series_data.index <= end_date_str)]
            
            if period_data.empty:
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
          
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'line', **kwargs) -> str:
        """Create FRED indicator chart.
        
        Args:
            chart_type: 'line' (default and only option for FRED)
            **kwargs: Additional chart options (baseline, positive_label, negative_label, etc.)
        """
        series_data = data['data']
        config = data['config']
        
        # FRED always uses line chart with baseline
        return create_fred_chart(
            data=series_data,
            label=label or config['name'],
            period=period,
            **kwargs
        )
    
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """Extract analysis metrics from FRED data."""
        series_data = data['data']
        
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
            'volatility': float(series_data.pct_change(fill_method=None).std() * (len(series_data) ** 0.5) * 100)
        }

