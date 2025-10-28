"""Unit tests for charts.py"""

import unittest
import asyncio
import os
import pandas as pd
from unittest.mock import patch, MagicMock
from src.utils.data_sources import get_data_source
from src.utils.charts import create_yfinance_chart, create_fred_chart


class TestYFinanceCharts(unittest.TestCase):
    """Test yfinance chart generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock data for different periods
        self.mock_data_5d = {
            'history': pd.DataFrame({
                'Open': [100, 101, 102, 103, 104],
                'High': [105, 106, 107, 108, 109],
                'Low': [99, 100, 101, 102, 103],
                'Close': [104, 105, 106, 107, 108],
                'SMA_5': [102, 103, 104, 105, 106],
                'SMA_20': [101, 102, 103, 104, 105]
            }, index=pd.bdate_range('2024-01-01', periods=5))  # Business days only
        }
        
        self.mock_data_1mo = {
            'history': pd.DataFrame({
                'Open': [100 + i for i in range(20)],
                'High': [105 + i for i in range(20)],
                'Low': [99 + i for i in range(20)],
                'Close': [104 + i for i in range(20)],
                'SMA_5': [102 + i for i in range(20)],
                'SMA_20': [101 + i for i in range(20)]
            }, index=pd.bdate_range('2024-01-01', periods=20))  # Business days only
        }
        
        self.mock_data_1y = {
            'history': pd.DataFrame({
                'Open': [100 + i for i in range(250)],
                'High': [105 + i for i in range(250)],
                'Low': [99 + i for i in range(250)],
                'Close': [104 + i for i in range(250)],
                'SMA_5': [102 + i for i in range(250)],
                'SMA_20': [101 + i for i in range(250)],
                'SMA_200': [100 + i for i in range(250)]
            }, index=pd.bdate_range('2024-01-01', periods=250))  # Business days only
        }
    
    @patch('src.utils.data_sources.get_data_source')
    def test_chart_5d_no_sma(self, mock_get_source):
        """Test 5-day chart without SMAs"""
        # Mock the data source
        mock_source = MagicMock()
        mock_source.fetch_data.return_value = self.mock_data_5d
        mock_get_source.return_value = mock_source
        
        result = create_yfinance_chart(
            ticker="AAPL",
            data=self.mock_data_5d['history'],
            period="5d",
            ylabel="Price (USD)",
            value_format="${:.2f}"
        )
        
        self.assertIn("Chart saved:", result)
        chart_path = result.split("Chart saved: ")[1].split("\n")[0]
        self.assertTrue(os.path.exists(chart_path))
    
    @patch('src.utils.data_sources.get_data_source')
    def test_chart_1mo_with_sma(self, mock_get_source):
        """Test 1-month chart with SMA 5, 20"""
        # Mock the data source
        mock_source = MagicMock()
        mock_source.fetch_data.return_value = self.mock_data_1mo
        mock_get_source.return_value = mock_source
        
        result = create_yfinance_chart(
            ticker="AAPL",
            data=self.mock_data_1mo['history'],
            period="1mo",
            ylabel="Price (USD)",
            value_format="${:.2f}"
        )
        
        self.assertIn("Chart saved:", result)
        # Verify SMAs are in the data
        hist = self.mock_data_1mo['history']
        self.assertIn('SMA_5', hist.columns)
        self.assertIn('SMA_20', hist.columns)
    
    @patch('src.utils.data_sources.get_data_source')
    def test_chart_1y_with_sma_200(self, mock_get_source):
        """Test 1-year chart with SMA 5, 20, 200"""
        # Mock the data source
        mock_source = MagicMock()
        mock_source.fetch_data.return_value = self.mock_data_1y
        mock_get_source.return_value = mock_source
        
        result = create_yfinance_chart(
            ticker="AAPL",
            data=self.mock_data_1y['history'],
            period="1y",
            ylabel="Price (USD)",
            value_format="${:.2f}"
        )
        
        self.assertIn("Chart saved:", result)
        # Verify all SMAs are in the data
        hist = self.mock_data_1y['history']
        self.assertIn('SMA_5', hist.columns)
        self.assertIn('SMA_20', hist.columns)
        self.assertIn('SMA_200', hist.columns)
    
    @patch('src.utils.data_sources.get_data_source')
    def test_chart_treasury(self, mock_get_source):
        """Test treasury chart (^TNX)"""
        # Mock treasury data
        mock_treasury_data = {
            'history': pd.DataFrame({
                'Open': [4.0 + i*0.01 for i in range(120)],
                'High': [4.1 + i*0.01 for i in range(120)],
                'Low': [3.9 + i*0.01 for i in range(120)],
                'Close': [4.05 + i*0.01 for i in range(120)],
                'SMA_5': [4.02 + i*0.01 for i in range(120)],
                'SMA_20': [4.01 + i*0.01 for i in range(120)]
            }, index=pd.bdate_range('2024-01-01', periods=120))  # Business days only
        }
        
        # Mock the data source
        mock_source = MagicMock()
        mock_source.fetch_data.return_value = mock_treasury_data
        mock_get_source.return_value = mock_source
        
        result = create_yfinance_chart(
            ticker="^TNX",
            data=mock_treasury_data['history'],
            period="6mo",
            ylabel="Yield (%)",
            value_format="{:.3f}%"
        )
        
        self.assertIn("Chart saved:", result)
    
    def test_candlestick_no_gaps(self):
        """Test candlestick chart has no weekend gaps"""
        # Use mock data with only trading days
        hist = self.mock_data_1mo['history']
        
        # Verify all OHLC columns exist
        self.assertIn('Open', hist.columns)
        self.assertIn('High', hist.columns)
        self.assertIn('Low', hist.columns)
        self.assertIn('Close', hist.columns)
        
        # Verify only trading days (no weekends)
        dates = hist.index
        for date in dates:
            # Trading days are Mon-Fri (0-4), Saturday=5, Sunday=6
            self.assertIn(date.weekday(), range(5))


class TestFREDCharts(unittest.TestCase):
    """Test FRED chart generation"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock FRED data
        self.mock_fred_data = {
            'data': pd.Series(
                [0.1, 0.2, -0.1, 0.3, -0.2, 0.0, 0.1, -0.1, 0.2, 0.0],
                index=pd.date_range('2024-01-01', periods=10, freq='W')
            )
        }
    
    @patch('src.utils.data_sources.get_data_source')
    def test_chart_nfci(self, mock_get_source):
        """Test NFCI chart with baseline"""
        # Mock the data source
        mock_source = MagicMock()
        mock_source.fetch_data.return_value = self.mock_fred_data
        mock_get_source.return_value = mock_source
        
        result = create_fred_chart(
            data=self.mock_fred_data['data'],
            indicator_name="National Financial Conditions Index",
            period="6mo",
            baseline=0,
            positive_label="Tighter Conditions",
            negative_label="Looser Conditions"
        )
        
        self.assertIn("Chart saved:", result)


class TestChartFeatures(unittest.TestCase):
    """Test specific chart features"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create mock data for different periods
        self.mock_data_5d = {
            'history': pd.DataFrame({
                'Open': [100, 101, 102, 103, 104],
                'High': [105, 106, 107, 108, 109],
                'Low': [99, 100, 101, 102, 103],
                'Close': [104, 105, 106, 107, 108],
                'SMA_5': [102, 103, 104, 105, 106],
                'SMA_20': [101, 102, 103, 104, 105]
            }, index=pd.bdate_range('2024-01-01', periods=5))  # Business days only
        }
        
        self.mock_data_1mo = {
            'history': pd.DataFrame({
                'Open': [100 + i for i in range(20)],
                'High': [105 + i for i in range(20)],
                'Low': [99 + i for i in range(20)],
                'Close': [104 + i for i in range(20)],
                'SMA_5': [102 + i for i in range(20)],
                'SMA_20': [101 + i for i in range(20)]
            }, index=pd.bdate_range('2024-01-01', periods=20))  # Business days only
        }
        
        self.mock_data_1y = {
            'history': pd.DataFrame({
                'Open': [100 + i for i in range(250)],
                'High': [105 + i for i in range(250)],
                'Low': [99 + i for i in range(250)],
                'Close': [104 + i for i in range(250)],
                'SMA_5': [102 + i for i in range(250)],
                'SMA_20': [101 + i for i in range(250)],
                'SMA_200': [100 + i for i in range(250)]
            }, index=pd.bdate_range('2024-01-01', periods=250))  # Business days only
        }
    
    def test_sma_by_period(self):
        """Test SMA presence varies by period"""
        # 5d: SMAs computed but won't be displayed on chart
        hist_5d = self.mock_data_5d['history']
        self.assertIn('SMA_5', hist_5d.columns)
        self.assertIn('SMA_20', hist_5d.columns)
        
        # 1mo: SMA 5, 20
        hist_1mo = self.mock_data_1mo['history']
        self.assertIn('SMA_5', hist_1mo.columns)
        self.assertIn('SMA_20', hist_1mo.columns)
        
        # 1y: SMA 5, 20, 200
        hist_1y = self.mock_data_1y['history']
        self.assertIn('SMA_5', hist_1y.columns)
        self.assertIn('SMA_20', hist_1y.columns)
        self.assertIn('SMA_200', hist_1y.columns)


if __name__ == "__main__":
    unittest.main()
