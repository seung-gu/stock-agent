"""YFinance data source for stocks, ETFs, and treasuries."""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from pandas.tseries.offsets import BDay
from typing import Any

from src.data_sources.base import APIDataSource
from src.utils.charts import create_yfinance_chart, create_line_chart
from src.utils.technical_indicators import calculate_sma


class YFinanceSource(APIDataSource):
    """Data source for stocks, ETFs, and treasuries via yfinance."""
    
    _cache: dict[str, Any] = {}
    
    def __init__(self):
        """Initialize with smart cache for API optimization."""
        super().__init__()
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert yfinance period string to approximate timedelta for display window."""
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
            print(f"Warning: Unsupported period '{period}', using default 6mo (200 days)")
            return timedelta(days=200)
        return period_map[period_lower]
    
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """Fetch data from yfinance with intelligent caching."""
        period_lower = (period or '').lower()
        cached = self._cache.get(symbol)
        if not period_lower:
            if cached and cached.get('period'):
                print(f"[YF][WARN] Empty period for {symbol}; defaulting to cached period '{cached['period']}'")
                period_lower = cached['period']
            else:
                print(f"[YF][WARN] Empty period for {symbol}; defaulting to '1y'")
                period_lower = '1y'
        
        if self._should_fetch(symbol, period_lower):
            print(f"[YF][API] Fetching data: symbol={symbol}, period={period_lower}")
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            
            if period_lower == 'max':
                hist = ticker.history(period='max')
            else:
                display_delta = self._period_to_timedelta(period_lower)
                start_display = end_date - display_delta
                
                max_window = 20 if period_lower in ['1mo', '3mo'] else 200
                safety_margin = 20
                fetch_start = pd.Timestamp(start_display.date()) - BDay(max_window + safety_margin)
                hist = ticker.history(start=fetch_start, end=end_date)
            
            if hist.empty:
                raise ValueError(f"No data found for {symbol} with period {period_lower}")
            
            # Normalize timezone
            try:
                hist.index = hist.index.tz_localize(None)
            except (TypeError, AttributeError):
                pass
            
            # Get info
            info = {}
            if cached and 'info' in cached:
                info = cached['info']
            else:
                try:
                    info = getattr(ticker, 'info', {}) or {}
                except Exception:
                    info = {}
            
            self._cache[symbol] = {
                'hist': hist,
                'info': info,
                'period': period_lower,
                'fetched_at': datetime.now()
            }
            cached = self._cache[symbol]
        else:
            if cached:
                print(f"[YF][CACHE] Using cached data: symbol={symbol}, cached_period={cached['period']} → requested={period_lower}")
        
        hist = cached['hist']
        info = cached['info']
        
        # Compute SMA columns
        if 'Close' in hist.columns:
            if 'SMA_5' not in hist.columns:
                hist['SMA_5'] = calculate_sma(hist, 5)
            if 'SMA_20' not in hist.columns:
                hist['SMA_20'] = calculate_sma(hist, 20)
            if 'SMA_200' not in hist.columns:
                hist['SMA_200'] = calculate_sma(hist, 200)

        # Slice to requested period
        if period_lower == 'max':
            hist_display = hist
        else:
            end_date = datetime.now()
            display_delta = self._period_to_timedelta(period_lower)
            start_display = (end_date - display_delta).date()
            start_display_ts = pd.Timestamp(start_display)
            first_valid_ts = None
            if 'SMA_200' in hist.columns:
                first_valid_ts = hist['SMA_200'].first_valid_index()
            effective_start = start_display_ts
            if first_valid_ts is not None and first_valid_ts > effective_start:
                effective_start = first_valid_ts
            pos = hist.index.searchsorted(effective_start)
            hist_display = hist.iloc[pos:]

        return {
            'data': hist_display,
            'info': info,
            'symbol': symbol
        }
    
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None, chart_type: str = 'candle', **kwargs) -> str:
        """Create stock/treasury chart.
        
        Args:
            chart_type: 'candle' (default, OHLCV candlestick) or 'line' (line chart)
            **kwargs: Additional chart options (ylabel, value_format, threshold_upper, etc.)
        """
        hist = data['data']
        info = data['info']
        
        if chart_type == 'candle':
            return create_yfinance_chart(
                data=hist,
                period=period,
                label=label or symbol,
                **kwargs
            )
        elif chart_type == 'line':
            # Support both raw OHLC data (use Close) and pre-calculated series (use as-is)
            hist_data = data['data']
            if 'Close' in hist_data.columns:
                # Raw OHLC data - use Close column
                line_data = hist_data['Close'].to_frame(name='Close')
                default_label = label or symbol
            else:
                # Pre-calculated series (Disparity, RSI, etc.) - use as-is
                line_data = hist_data
                default_label = label or symbol
            
            return create_line_chart(
                data=line_data,
                label=default_label,
                period=period,
                **kwargs
            )
        else:
            raise ValueError(f"Unsupported chart_type: {chart_type}. Use 'candle' or 'line'.")
    
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
        """Extract basic analysis metrics from yfinance data."""
        hist = data['data']
        
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
            'volatility': float(hist['Close'].pct_change(fill_method=None).std() * (len(hist) ** 0.5) * 100)
        }

