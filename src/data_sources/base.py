"""
Base classes for data sources.

Provides abstract base classes for API and Web scraping data sources.
"""

import pandas as pd
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any
from pathlib import Path
import json


class DataSource(ABC):
    """Base class for all data sources."""
    
    def __init__(self):
        """Initialize data source."""
        pass
    
    @staticmethod
    def _get_period_rank(period: str) -> int:
        """Get period rank for comparison (higher = longer)."""
        period_ranks = {
            '5d': 1, '1mo': 2, '3mo': 3, '6mo': 4, 
            '1y': 5, '2y': 6, '5y': 7, '10y': 8, 'max': 9
        }
        return period_ranks.get(period.lower(), 5)  # Default to 1y
    
    def _should_fetch(self, symbol: str, period: str) -> bool:
        """Determine if we need to fetch data from API."""
        cached = self._cache.get(symbol)
        if not cached:
            return True
        if self._get_period_rank(period) > self._get_period_rank(cached['period']):
            return True
        return False
    
    @abstractmethod
    async def fetch_data(self, symbol: str, period: str) -> dict[str, Any]:
        """
        Fetch raw data from the source.
        
        Args:
            symbol: Symbol or indicator code
            period: Time period (5d, 1mo, 6mo, etc.)
            
        Returns:
            Dictionary with data and metadata
        """
        pass
    
    @abstractmethod
    async def create_chart(self, data: dict[str, Any], symbol: str, period: str, label: str = None) -> str:
        """
        Create chart from fetched data.
        
        Args:
            data: Data returned from fetch_data()
            symbol: Symbol or indicator code
            period: Time period
            label: Human-readable label for chart title (optional)
            
        Returns:
            Chart information string with path
        """
        pass
    
    @abstractmethod
    def get_analysis(self, data: dict[str, Any], period: str) -> dict[str, Any]:
        """
        Extract analysis metadata from data.
        
        Args:
            data: Data returned from fetch_data()
            period: Time period
            
        Returns:
            Dictionary with analysis metrics
        """
        pass
    
    @abstractmethod
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Convert period string to timedelta. Must be implemented by subclasses."""
        pass
    
    def get_actual_period_approx(self, data: dict[str, Any]) -> str:
        """
        Find closest matching period by comparing actual days with standard periods.
        
        Args:
            data: Data returned from fetch_data()
            
        Returns:
            Approximated period string (e.g., '1y', '6mo')
        """
        data_with_index = data['data']
        
        # Remove NaN values to get actual valid data range
        if hasattr(data_with_index, 'dropna'):
            data_with_index = data_with_index.dropna()
        
        if len(data_with_index) == 0:
            return "5d"  # Default fallback
        
        actual_days = (data_with_index.index[-1] - data_with_index.index[0]).days
        
        # Try all standard periods and find closest match
        periods = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"]
        
        best_match = periods[0]
        min_diff = float('inf')
        
        for period in periods:
            expected_days = self._period_to_timedelta(period).days
            diff = abs(actual_days - expected_days)
            if diff < min_diff:
                min_diff = diff
                best_match = period

        return best_match


class APIDataSource(DataSource):
    """Base class for API-based data sources (YFinance, FRED, Finnhub)."""
    
    def __init__(self):
        """Initialize with memory cache."""
        super().__init__()  # Memory-based cache for API sources


class WebDataSource(DataSource):
    """Base class for web scraping data sources (Investing, AAII, YCharts)."""
    
    # Common browser headers for web scraping
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self):
        """Initialize with file-based cache."""
        super().__init__()
        self._cache_file: Path | None = None
    
    def _load_local_cache(self, symbol: str, log_prefix: str) -> tuple[pd.Series | None, bool]:
        """Load historical data from local JSON file (unified for all web sources)."""
        if not self._cache_file.exists():
            print(f"[{log_prefix}][CACHE] Cache file not found: {self._cache_file}")
            return None, False
        try:
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
            
            symbol_data = all_data.get(symbol, [])
            if not symbol_data:
                print(f"[{log_prefix}][CACHE] No data for {symbol} in cache")
                return None, False
            
            is_validated = all_data.get('_validated', False)
            # Filter out NaN values (both actual NaN and string "NaN")
            data_dict = {}
            for item in symbol_data:
                value = item['value']
                # Skip NaN values (both actual NaN and string "NaN")
                if isinstance(value, str) and value.lower() == 'nan':
                    continue
                if pd.isna(value):
                    continue
                data_dict[pd.to_datetime(item['date'])] = value
            
            # Check if all data was filtered out (all NaN)
            if not data_dict:
                print(f"[{log_prefix}][CACHE] All data for {symbol} was NaN, cache invalid")
                return None, False
            
            series = pd.Series(data_dict).sort_index()
            
            print(f"[{log_prefix}][CACHE] Loaded {len(series)} records for {symbol}, latest: {series.index[-1].date()}, validated: {is_validated}")
            return series, is_validated
        except Exception as e:
            print(f"[{log_prefix}][CACHE] Error loading cache: {e}")
            return None, False
    
    def _save_local_cache(self, symbol: str, data: pd.Series, is_validated: bool, log_prefix: str):
        """Save historical data to local JSON file (unified for all web sources)."""
        self._cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self._cache_file.exists():
            with open(self._cache_file, 'r') as f:
                all_data = json.load(f)
        else:
            all_data = {}
        
        # Filter out NaN values - don't save NaN, preserve existing good values
        # Also remove duplicate dates (keep last occurrence)
        symbol_data_dict = {}
        existing_dates = set()
        if symbol in all_data:
            existing_dates = {item['date'] for item in all_data[symbol]}
        
        for d, v in data.items():
            date_str = d.strftime('%Y-%m-%d')
            if pd.notna(v):  # Only save non-NaN values
                symbol_data_dict[date_str] = {'date': date_str, 'value': float(v)}
            elif date_str in existing_dates:
                # Keep existing value if it exists and new value is NaN
                existing_item = next((item for item in all_data[symbol] if item['date'] == date_str), None)
                if existing_item and pd.notna(existing_item.get('value')):
                    symbol_data_dict[date_str] = existing_item
                    print(f"[{log_prefix}][CACHE] Preserved existing value for {date_str} (new value was NaN)")
        
        # Convert dict to list (duplicates already removed by dict key)
        symbol_data = list(symbol_data_dict.values())
        # Sort by date
        symbol_data.sort(key=lambda x: x['date'])
        
        all_data[symbol] = symbol_data
        all_data['_validated'] = is_validated
        
        with open(self._cache_file, 'w') as f:
            json.dump(all_data, f, indent=2)
        
        print(f"[{log_prefix}][CACHE] Saved {len(symbol_data)} records for {symbol}, validated: {is_validated}")
    
    def _fetch_with_cache_and_scrape(
        self,
        symbol: str,
        period: str,
        load_cache_fn,
        save_cache_fn,
        scrape_fn,
        build_result_fn,
        date_offset_tolerance: int = 0
    ) -> dict[str, Any]:
        """
        Common fetch logic with caching and scraping for file-based sources.
        
        Args:
            symbol: Symbol to fetch
            period: Time period
            load_cache_fn: Function to load cache, returns (data, is_validated)
            save_cache_fn: Function to save cache, takes (data, is_validated)
            scrape_fn: Function to scrape data, returns Series
            build_result_fn: Function to build final result dict, takes (period_data, merged)
            date_offset_tolerance: Days tolerance for date offset (default: 0)
        """
        period = period or '1y'
        print(f"[CACHE][FETCH] symbol={symbol}, period={period}")
        
        # Load local cache with validation flag
        local, is_validated = load_cache_fn()
        
        # Check if cache is up-to-date (skip scrape if latest cached date >= last business day)
        today = datetime.now().date()
        weekday = today.weekday()  # 0=Mon, ... 6=Sun
        # Sat(5): 5-4=1 day back → Fri, Sun(6): 6-4=2 days back → Fri
        last_bday = today - timedelta(days=weekday - 4 if weekday > 4 else 0)
        
        if local is not None and len(local) > 0 and is_validated:
            latest_cached_date = local.index[-1].date()
            if latest_cached_date >= last_bday:
                print(f"[CACHE] Up-to-date (cached: {latest_cached_date} >= last bday: {last_bday}), skipping scrape")
                merged = local
                # Skip to return section
                end_date = datetime.now()
                start_date = end_date - self._period_to_timedelta(period)
                period_data = merged[merged.index >= start_date]
                print(f"[CACHE][RETURN] Returning {len(period_data)} records for period {period}")
                return build_result_fn(period_data if len(period_data) > 0 else merged, merged)
        
        # Scrape to check latest available date
        print(f"[SCRAPE] Fetching data")
        try:
            scraped = scrape_fn()
            latest_scraped_date = scraped.index[-1].date()
        except Exception as e:
            print(f"[SCRAPE] Failed to scrape: {e}")
            # If scraping fails and we have cache, use cache
            if local is not None and len(local) > 0:
                print(f"[CACHE] Using cached data due to scrape failure")
                merged = local
                end_date = datetime.now()
                start_date = end_date - self._period_to_timedelta(period)
                period_data = merged[merged.index >= start_date]
                print(f"[CACHE][RETURN] Returning {len(period_data)} records for period {period}")
                return build_result_fn(period_data if len(period_data) > 0 else merged, merged)
            else:
                # No cache and scraping failed
                raise ValueError(f"Failed to fetch data: {e}")
        
        # Determine if we need to update cache
        need_update = True
        
        if local is not None and len(local) > 0:
            latest_cached_date = local.index[-1].date()
            date_diff = abs((latest_scraped_date - latest_cached_date).days)
            
            # If date difference is within tolerance, consider it as same data (offset issue)
            if date_diff <= date_offset_tolerance:
                print(f"[CACHE] Date offset within {date_offset_tolerance} days (cached: {latest_cached_date}, scraped: {latest_scraped_date}, diff: {date_diff} days), using cache")
                need_update = False
                merged = local
            elif is_validated and latest_cached_date >= latest_scraped_date:
                # validated + cache has all scraped data → no update needed
                print(f"[CACHE] Validated and up-to-date (cached: {latest_cached_date}, scraped: {latest_scraped_date}), using cache")
                need_update = False
                merged = local
            elif is_validated and latest_cached_date < latest_scraped_date:
                # validated + new data available → update needed
                print(f"[CACHE] Validated but outdated (cached: {latest_cached_date}, scraped: {latest_scraped_date}), will update")
            else:
                # not validated → update needed
                print(f"[CACHE] Not validated, will update and validate")
        else:
            print(f"[CACHE] No local cache found, will create")
        
        # Update cache if needed
        if need_update:
            if local is not None:
                # Merge: keep all local data + add/update with new scraped data
                # If tolerance=0: update existing dates with scraped values, add new dates
                # If tolerance>0: skip dates within tolerance (preserve local), add dates outside tolerance
                merged = local.copy()
                tolerance_days = date_offset_tolerance
                
                # Sort scraped dates to process them in order
                scraped_sorted = scraped.sort_index()
                
                for scraped_date, scraped_value in scraped_sorted.items():
                    # Skip NaN values - don't add them to merged data
                    if pd.isna(scraped_value):
                        continue
                    
                    # Check if scraped date is within tolerance of any existing local date
                    # Use local.index (not merged.index) to avoid checking against newly added dates
                    if tolerance_days > 0:
                        # If tolerance > 0, skip dates within tolerance (preserve local data for offset dates)
                        # Use < (not <=) to allow exact matches (0 days) to be updated with newer scraped data
                        if any(0 < abs((scraped_date - local_date).days) <= tolerance_days for local_date in local.index):
                            continue
                    
                    # Add or update the date with scraped value (more recent)
                    merged[scraped_date] = scraped_value
                    if scraped_date not in local.index:
                        print(f"[MERGE] Added new date: {scraped_date}")
                
                merged = merged.sort_index()
            else:
                # Remove duplicates from scraped data too
                merged = scraped[~scraped.index.duplicated(keep='last')].sort_index()
            
            # Save with validation flag (validated)
            save_cache_fn(merged, is_validated=True)
        
        # Slice to requested period
        end_date = datetime.now()
        start_date = end_date - self._period_to_timedelta(period)
        period_data = merged[merged.index >= start_date]
        
        print(f"[CACHE][RETURN] Returning {len(period_data)} records for period {period}")
        
        return build_result_fn(period_data if len(period_data) > 0 else merged, merged)

