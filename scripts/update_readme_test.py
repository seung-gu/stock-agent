#!/usr/bin/env python3
"""Unit tests for update_readme.py"""

import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.update_readme import ReadmeUpdater


class TestReadmeUpdater(unittest.TestCase):
    """Test ReadmeUpdater class"""
    
    def setUp(self):
        """Create temporary README file for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.readme_path = Path(self.temp_dir) / "readme.md"
        
        # Create sample README content
        self.sample_content = """# Test Project

## Quick Start

### Recent Reports
- [2025-12-03](https://notion.so/test-1)
- [2025-12-02](https://notion.so/test-2)
- [2025-12-01](https://notion.so/test-3)

---

## Other Section
Some content here.
"""
        self.readme_path.write_text(self.sample_content, encoding='utf-8')
    
    def tearDown(self):
        """Clean up temporary files"""
        if self.readme_path.exists():
            os.remove(self.readme_path)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_update_recent_reports_adds_new_entry(self):
        """Test that new report is added at the top"""
        updater = ReadmeUpdater(str(self.readme_path))
        updater.update_recent_reports("https://notion.so/test-new")
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Check new entry is at the top
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.assertIn(f"[{date_str}](https://notion.so/test-new)", content)
        
        # Check old entries still exist
        self.assertIn("[2025-12-03]", content)
        self.assertIn("[2025-12-02]", content)
    
    def test_update_recent_reports_replaces_same_date(self):
        """Test that same date entry is replaced"""
        # Create README with today's date
        date_str = datetime.now().strftime('%Y-%m-%d')
        content_with_today = f"""### Recent Reports
- [{date_str}](https://notion.so/old-url)
- [2025-12-02](https://notion.so/test-2)

---
"""
        self.readme_path.write_text(content_with_today, encoding='utf-8')
        
        updater = ReadmeUpdater(str(self.readme_path))
        updater.update_recent_reports("https://notion.so/new-url")
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Check old URL is replaced
        self.assertNotIn("old-url", content)
        self.assertIn("new-url", content)
        
        # Check only one entry for today
        self.assertEqual(content.count(f"[{date_str}]"), 1)
    
    def test_update_recent_reports_keeps_max_10_entries(self):
        """Test that only last 10 reports are kept"""
        # Create README with 12 entries
        reports_list = [f"- [2025-12-{i:02d}](https://notion.so/test-{i})" for i in range(1, 13)]
        content_with_many = f"""### Recent Reports
{chr(10).join(reports_list)}

---
"""
        self.readme_path.write_text(content_with_many, encoding='utf-8')
        
        updater = ReadmeUpdater(str(self.readme_path))
        updater.update_recent_reports("https://notion.so/new")
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        lines = [line for line in content.split('\n') if line.strip().startswith('- [')]
        
        # Should have exactly 10 entries (new one + 9 old ones)
        self.assertEqual(len(lines), 10)
    
    def test_update_heatmap_creates_new_section(self):
        """Test that heatmap section is created if not exists"""
        updater = ReadmeUpdater(str(self.readme_path))
        updater.update_heatmap("https://r2.example.com/heatmap.png")
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Check heatmap section exists
        self.assertIn("### Latest Indicator Heatmap", content)
        self.assertIn("![Indicator Heatmap](https://r2.example.com/heatmap.png)", content)
        
        # Check date is included
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.assertIn(f"*Updated: {date_str}*", content)
    
    def test_update_heatmap_updates_existing_section(self):
        """Test that existing heatmap section is updated"""
        # Create README with existing heatmap
        content_with_heatmap = """### Recent Reports
- [2025-12-03](https://notion.so/test-1)

### Latest Indicator Heatmap
![Indicator Heatmap](https://r2.example.com/old-heatmap.png)

*Updated: 2025-12-01*

---
"""
        self.readme_path.write_text(content_with_heatmap, encoding='utf-8')
        
        updater = ReadmeUpdater(str(self.readme_path))
        updater.update_heatmap("https://r2.example.com/new-heatmap.png")
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Check old heatmap is replaced
        self.assertNotIn("old-heatmap.png", content)
        self.assertIn("new-heatmap.png", content)
        
        # Check date is updated
        date_str = datetime.now().strftime('%Y-%m-%d')
        self.assertIn(f"*Updated: {date_str}*", content)
        
        # Check only one heatmap section
        self.assertEqual(content.count("### Latest Indicator Heatmap"), 1)
    
    def test_multiple_updates_in_sequence(self):
        """Test multiple updates work correctly"""
        updater = ReadmeUpdater(str(self.readme_path))
        
        # Update report
        updater.update_recent_reports("https://notion.so/report-1")
        
        # Update heatmap
        updater.update_heatmap("https://r2.example.com/heatmap-1.png")
        
        # Save
        updater.save()
        
        content = self.readme_path.read_text(encoding='utf-8')
        
        # Check both updates are present
        self.assertIn("https://notion.so/report-1", content)
        self.assertIn("https://r2.example.com/heatmap-1.png", content)


if __name__ == "__main__":
    unittest.main()

