"""Finnhub data source for company fundamentals."""

import os
import finnhub
from datetime import datetime, timedelta
from typing import Any
from dotenv import load_dotenv

from src.data_sources.base import APIDataSource

load_dotenv()


class FinnhubSource(APIDataSource):
    """Data source for company fundamentals via Finnhub API."""
    
    _cache: dict[str, Any] = {}
    
    def __init__(self):
        super().__init__()
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of Finnhub client."""
        if self._client is None:
            api_key = os.getenv('FINNHUB_API_KEY')
            if not api_key:
                raise ValueError("FINNHUB_API_KEY not found in environment variables")
            self._client = finnhub.Client(api_key=api_key)
        return self._client
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Not used for fundamentals data."""
        return timedelta(days=365)
    
    def fetch_data(self, symbol: str, period: str = None) -> dict[str, Any]:
        """Fetch Forward P/E data from Finnhub."""
        try:
            quote = self.client.quote(symbol)
            current_price = quote.get('c') if quote else None
            
            if not current_price:
                return {
                    'symbol': symbol,
                    'current_price': None,
                    'forward_eps_ntm': None,
                    'error': 'Failed to fetch current price'
                }
            
            forward_eps_ntm = None
            try:
                past_earnings = self.client.company_earnings(symbol, limit=1)
                last_actual = past_earnings[0].get('actual', 0) if past_earnings else 0
                
                from_date = datetime.now().strftime('%Y-%m-%d')
                to_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
                
                earnings_cal = self.client.earnings_calendar(
                    _from=from_date,
                    to=to_date,
                    symbol=symbol,
                    international=False
                )
                
                estimates = earnings_cal.get('earningsCalendar', [])
                next_3_estimates = sum(e.get('epsEstimate', 0) for e in estimates[:3])
                
                forward_eps_ntm = last_actual + next_3_estimates
                
            except Exception as e:
                print(f"[FINNHUB] Could not fetch forward estimates: {e}")
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'forward_eps_ntm': forward_eps_ntm,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[FINNHUB] Error fetching data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'current_price': None,
                'forward_eps_ntm': None,
                'error': str(e)
            }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'line', **kwargs) -> str:
        """Not implemented for fundamentals data."""
        return f"Chart generation not supported for Finnhub fundamentals data"
    
    def get_analysis(self, data: dict[str, Any], period: str = None) -> dict[str, Any]:
        """Calculate Forward P/E (NTM) from fetched data."""
        current_price = data.get('current_price')
        forward_eps_ntm = data.get('forward_eps_ntm')
        forward_pe_ntm = None
        
        if current_price and forward_eps_ntm and forward_eps_ntm > 0:
            forward_pe_ntm = current_price / forward_eps_ntm
        
        return {
            'symbol': data.get('symbol'),
            'current_price': current_price,
            'forward_eps_ntm': forward_eps_ntm,
            'forward_pe_ntm': forward_pe_ntm
        }

