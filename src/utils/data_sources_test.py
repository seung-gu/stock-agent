"""Unit tests for data_sources.py"""

import unittest
import asyncio
import pandas as pd
from unittest.mock import patch, MagicMock
from src.utils.data_sources import get_data_source, YFinanceSource, FREDSource


class TestYFinanceSource(unittest.TestCase):
    """Test YFinanceSource functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.source = YFinanceSource()
        
        # Create mock data - using recent dates to ensure they pass date slicing
        from datetime import datetime, timedelta
        end_date = datetime.now()
        
        self.mock_data_5d = {
            'history': pd.DataFrame({
                'Open': [100, 101, 102, 103, 104],
                'High': [105, 106, 107, 108, 109],
                'Low': [99, 100, 101, 102, 103],
                'Close': [104, 105, 106, 107, 108],
                'SMA_5': [102, 103, 104, 105, 106],
                'SMA_20': [101, 102, 103, 104, 105]
            }, index=pd.date_range(end=end_date, periods=5, freq='D'))
        }
        
        self.mock_data_1mo = {
            'history': pd.DataFrame({
                'Open': [100 + i for i in range(30)],
                'High': [105 + i for i in range(30)],
                'Low': [99 + i for i in range(30)],
                'Close': [104 + i for i in range(30)],
                'SMA_5': [102 + i for i in range(30)],
                'SMA_20': [101 + i for i in range(30)]
            }, index=pd.date_range(end=end_date, periods=30, freq='D'))
        }
        
        self.mock_data_1y = {
            'history': pd.DataFrame({
                'Open': [100 + i*0.1 for i in range(650)],
                'High': [105 + i*0.1 for i in range(650)],
                'Low': [99 + i*0.1 for i in range(650)],
                'Close': [104 + i*0.1 for i in range(650)],
                'SMA_5': [102 + i*0.1 for i in range(650)],
                'SMA_20': [101 + i*0.1 for i in range(650)],
                'SMA_200': [100 + i*0.1 for i in range(650)]
            }, index=pd.date_range(end=end_date, periods=650, freq='D'))
        }
    
    @patch('yfinance.Ticker')
    def test_fetch_5d(self, mock_ticker_class):
        """Test fetching 5-day data"""
        # Mock yfinance Ticker and its history method
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.mock_data_5d['history']
        mock_ticker_class.return_value = mock_ticker
        
        async def run():
            data = await self.source.fetch_data("AAPL", "5d")
            hist = data['history']
            self.assertIsNotNone(hist)
            self.assertGreater(len(hist), 0)
            self.assertIn('Close', hist.columns)
            self.assertIn('SMA_5', hist.columns)
            self.assertIn('SMA_20', hist.columns)
        
        asyncio.run(run())
    
    @patch('yfinance.Ticker')
    def test_fetch_1mo(self, mock_ticker_class):
        """Test fetching 1-month data"""
        # Mock yfinance Ticker and its history method
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.mock_data_1mo['history']
        mock_ticker_class.return_value = mock_ticker
        
        async def run():
            data = await self.source.fetch_data("AAPL", "1mo")
            hist = data['history']
            self.assertIsNotNone(hist)
            self.assertGreater(len(hist), 0)
            self.assertIn('SMA_5', hist.columns)
            self.assertIn('SMA_20', hist.columns)
        
        asyncio.run(run())
    
    @patch('yfinance.Ticker')
    def test_fetch_1y(self, mock_ticker_class):
        """Test fetching 1-year data with SMA 200"""
        # Mock yfinance Ticker and its history method
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = self.mock_data_1y['history']
        mock_ticker_class.return_value = mock_ticker
        
        async def run():
            data = await self.source.fetch_data("AAPL", "1y")
            hist = data['history']
            self.assertIsNotNone(hist)
            self.assertGreater(len(hist), 0)
            self.assertIn('SMA_5', hist.columns)
            self.assertIn('SMA_20', hist.columns)
            self.assertIn('SMA_200', hist.columns)
        
        asyncio.run(run())
    
    def test_get_analysis(self):
        """Test analysis metrics extraction"""
        # Use mock data directly
        analysis = self.source.get_analysis(self.mock_data_1mo, "1mo")
        
        self.assertIn('start', analysis)
        self.assertIn('end', analysis)
        self.assertIn('change_pct', analysis)
        self.assertIn('high', analysis)
        self.assertIn('low', analysis)
        self.assertIn('volatility', analysis)
    
    def test_unsupported_period_warning(self):
        """Test unsupported period shows warning and uses default"""
        with patch('builtins.print') as mock_print:
            # Test the period mapping method directly
            result = self.source._period_to_timedelta("ytd")
            # Should print warning and return default
            mock_print.assert_called()
            self.assertIsNotNone(result)


class TestFREDSource(unittest.TestCase):
    """Test FREDSource functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.source = FREDSource()
        
        # Create mock FRED data
        self.mock_fred_data = {
            'data': pd.Series(
                [0.1, 0.2, -0.1, 0.3, -0.2, 0.0, 0.1, -0.1, 0.2, 0.0],
                index=pd.date_range('2024-01-01', periods=10, freq='W')
            )
        }
    
    @patch('fredapi.Fred.get_series')
    def test_fetch_nfci(self, mock_get_series):
        """Test fetching NFCI data"""
        # Mock FRED response
        mock_get_series.return_value = self.mock_fred_data['data']
        
        async def run():
            data = await self.source.fetch_data("NFCI", "6mo")
            series = data['data']
            self.assertIsNotNone(series)
            self.assertGreater(len(series), 0)
        
        asyncio.run(run())
    
    def test_get_analysis(self):
        """Test FRED analysis extraction"""
        # Use mock data directly
        analysis = self.source.get_analysis(self.mock_fred_data, "6mo")
        
        self.assertIn('latest', analysis)
        self.assertIn('latest_date', analysis)


class TestDataSourceFactory(unittest.TestCase):
    """Test data source factory function"""
    
    def test_get_yfinance_source(self):
        """Test getting yfinance source"""
        source = get_data_source("yfinance")
        self.assertIsNotNone(source)
        self.assertEqual(source.__class__.__name__, "YFinanceSource")
    
    def test_get_fred_source(self):
        """Test getting FRED source"""
        source = get_data_source("fred")
        self.assertIsNotNone(source)
        self.assertEqual(source.__class__.__name__, "FREDSource")
    
    def test_invalid_source(self):
        """Test invalid source raises error"""
        with self.assertRaises(ValueError):
            get_data_source("invalid_source")


if __name__ == "__main__":
    unittest.main()
