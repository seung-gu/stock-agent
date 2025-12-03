"""Unit tests for score collection and persistence service"""

import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd

from src.services.score_service import collect_scores, save_scores_to_csv
from src.types.analysis_report import AnalysisReport, IndicatorScore


class TestCollectScores(unittest.TestCase):
    """Test cases for collect_scores function"""
    
    def test_collect_scores_with_single_report(self):
        """Test collecting scores from a single report"""
        score = IndicatorScore(agent="VIX", indicator="VIX", value=3)
        report = AnalysisReport(
            title="VIX Analysis",
            content="Test content",
            score=[score]
        )
        
        result = collect_scores([report])
        
        self.assertEqual(result, {"VIX": 3})
    
    def test_collect_scores_with_multiple_indicators(self):
        """Test collecting scores from report with multiple indicators"""
        scores = [
            IndicatorScore(agent="S&P 500", indicator="RSI(14)", value=4),
            IndicatorScore(agent="S&P 500", indicator="Disparity(200)", value=3)
        ]
        report = AnalysisReport(
            title="S&P 500 Analysis",
            content="Test content",
            score=scores
        )
        
        result = collect_scores([report])
        
        self.assertEqual(result, {
            "S&P 500_RSI(14)": 4,
            "S&P 500_Disparity(200)": 3
        })
    
    def test_collect_scores_with_multiple_reports(self):
        """Test collecting scores from multiple reports"""
        report1 = AnalysisReport(
            title="VIX",
            content="Test",
            score=[IndicatorScore(agent="VIX", indicator="VIX", value=3)]
        )
        report2 = AnalysisReport(
            title="PutCall",
            content="Test",
            score=[IndicatorScore(agent="PutCall", indicator="PutCall", value=2)]
        )
        
        result = collect_scores([report1, report2])
        
        self.assertEqual(result, {"VIX": 3, "PutCall": 2})
    
    def test_collect_scores_with_empty_scores(self):
        """Test collecting scores from reports with no scores"""
        report = AnalysisReport(
            title="No scores",
            content="Test content",
            score=[]
        )
        
        result = collect_scores([report])
        
        self.assertEqual(result, {})
    
    def test_collect_scores_with_mixed_reports(self):
        """Test collecting scores from mix of reports with and without scores"""
        report1 = AnalysisReport(
            title="With score",
            content="Test",
            score=[IndicatorScore(agent="VIX", indicator="VIX", value=4)]
        )
        report2 = AnalysisReport(
            title="Without score",
            content="Test",
            score=[]
        )
        
        result = collect_scores([report1, report2])
        
        self.assertEqual(result, {"VIX": 4})


class TestSaveScoresToCSV(unittest.TestCase):
    """Test cases for save_scores_to_csv function"""
    
    @patch('src.services.score_service.write_csv_to_cloud')
    @patch('src.services.score_service.read_csv_from_cloud')
    def test_save_scores_to_new_csv(self, mock_read, mock_write):
        """Test saving scores when no existing CSV exists"""
        mock_read.return_value = None
        
        report = AnalysisReport(
            title="Test",
            content="Test",
            score=[IndicatorScore(agent="VIX", indicator="VIX", value=3)]
        )
        
        save_scores_to_csv([report], cloud_path="test/result.csv")
        
        # Verify write was called
        self.assertTrue(mock_write.called)
        
        # Check the DataFrame structure
        call_args = mock_write.call_args
        df = call_args[0][0]
        
        self.assertIn('date', df.columns)
        self.assertIn('VIX', df.columns)
        self.assertEqual(df['VIX'].iloc[0], 3)
    
    @patch('src.services.score_service.write_csv_to_cloud')
    @patch('src.services.score_service.read_csv_from_cloud')
    def test_save_scores_append_new_date(self, mock_read, mock_write):
        """Test appending scores for a new date"""
        # Mock existing CSV
        existing_df = pd.DataFrame({
            'date': ['2025-01-01'],
            'VIX': [2]
        })
        mock_read.return_value = existing_df
        
        report = AnalysisReport(
            title="Test",
            content="Test",
            score=[IndicatorScore(agent="VIX", indicator="VIX", value=4)]
        )
        
        save_scores_to_csv([report], cloud_path="test/result.csv")
        
        # Verify write was called
        self.assertTrue(mock_write.called)
        
        # Check the DataFrame has 2 rows
        call_args = mock_write.call_args
        df = call_args[0][0]
        
        self.assertEqual(len(df), 2)
        self.assertEqual(df['VIX'].tolist(), [2, 4])
    
    @patch('src.services.score_service.write_csv_to_cloud')
    @patch('src.services.score_service.read_csv_from_cloud')
    def test_save_scores_merge_same_date(self, mock_read, mock_write):
        """Test merging scores for the same date"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Mock existing CSV with today's date
        existing_df = pd.DataFrame({
            'date': [today],
            'VIX': [2]
        })
        mock_read.return_value = existing_df
        
        # New score for a different indicator
        report = AnalysisReport(
            title="Test",
            content="Test",
            score=[IndicatorScore(agent="PutCall", indicator="PutCall", value=3)]
        )
        
        save_scores_to_csv([report], cloud_path="test/result.csv")
        
        # Verify write was called
        self.assertTrue(mock_write.called)
        
        # Check both columns exist
        call_args = mock_write.call_args
        df = call_args[0][0]
        
        self.assertEqual(len(df), 1)  # Still one row (same date)
        self.assertIn('VIX', df.columns)
        self.assertIn('PutCall', df.columns)
        self.assertEqual(df['VIX'].iloc[0], 2)
        self.assertEqual(df['PutCall'].iloc[0], 3)
    
    @patch('src.services.score_service.write_csv_to_cloud')
    @patch('src.services.score_service.read_csv_from_cloud')
    def test_save_scores_with_no_scores(self, mock_read, mock_write):
        """Test that nothing is saved when there are no scores"""
        report = AnalysisReport(
            title="Test",
            content="Test",
            score=[]
        )
        
        save_scores_to_csv([report], cloud_path="test/result.csv")
        
        # Verify write was NOT called
        self.assertFalse(mock_write.called)
    
    @patch('src.services.score_service.write_csv_to_cloud')
    @patch('src.services.score_service.read_csv_from_cloud')
    def test_save_scores_handles_exception(self, mock_read, mock_write):
        """Test that exceptions are handled gracefully"""
        mock_read.side_effect = Exception("Cloud error")
        
        report = AnalysisReport(
            title="Test",
            content="Test",
            score=[IndicatorScore(agent="VIX", indicator="VIX", value=3)]
        )
        
        # Should not raise exception
        try:
            save_scores_to_csv([report], cloud_path="test/result.csv")
        except Exception:
            self.fail("save_scores_to_csv raised an exception")


def run_tests():
    """Run all tests"""
    unittest.main()


if __name__ == "__main__":
    run_tests()

