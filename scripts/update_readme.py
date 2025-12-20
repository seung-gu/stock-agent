#!/usr/bin/env python3
"""Update README with latest report link and indicator heatmap
This runs only when github actions is triggered
"""

import sys
import os
import re
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.generate_indicator_heatmap import generate_indicator_heatmap


class ReadmeUpdater:
    """Manages README updates for reports and heatmaps"""
    
    def __init__(self, readme_path: str = "readme.md"):
        self.readme_path = readme_path
        self.date_str = datetime.now().strftime('%Y-%m-%d')
        self.content = self._read_readme()
    
    def _read_readme(self) -> str:
        """Read current README content"""
        with open(self.readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _save_readme(self):
        """Save updated README content"""
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(self.content)
    
    def update_recent_reports(self, notion_url: str):
        """Update Recent Reports section with new report link"""
        new_entry = f"- [{self.date_str}]({notion_url})"
        pattern = r'(### Recent Reports.*?\n)(.*?)(\n###|\n---|\Z)'
        
        def replace(match):
            header, body, next_section = match.groups()
            
            # Extract existing links
            lines = body.strip().split('\n')
            links = [line for line in lines if line.strip().startswith('-')]
            
            # Remove duplicate date and add new entry
            links = [link for link in links if f"[{self.date_str}]" not in link]
            links.insert(0, new_entry)
            links = links[:10]  # Keep last 10
            
            return header + '\n'.join(links) + '\n' + next_section
        
        self.content = re.sub(pattern, replace, self.content, flags=re.DOTALL)
        print(f"✅ README updated with report: {notion_url}")
    
    def update_heatmap(self, heatmap_url: str):
        """Update Latest Indicator Heatmap section"""
        heatmap_content = f"![Indicator Heatmap]({heatmap_url})\n\n*Updated: {self.date_str}*"
        pattern = r'(### Latest Indicator Heatmap\n)(.*?)(\n###|\n---|\Z)'
        
        def replace(match):
            header, _, next_section = match.groups()
            return header + heatmap_content + '\n' + next_section
        
        # Update existing or insert new section
        if re.search(pattern, self.content, flags=re.DOTALL):
            self.content = re.sub(pattern, replace, self.content, flags=re.DOTALL)
        else:
            insert_pattern = r'(### Recent Reports\n(?:.*?\n)*?)(\n---|\n###)'
            insert_content = f"\n### Latest Indicator Heatmap\n{heatmap_content}\n"
            self.content = re.sub(insert_pattern, rf'\1{insert_content}\2', self.content, flags=re.DOTALL)
        
        print(f"✅ README updated with heatmap: {heatmap_url}")
    
    def save(self):
        """Save all changes"""
        self._save_readme()


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python update_readme.py <notion_url>")
        sys.exit(1)
    
    notion_url = sys.argv[1]
    updater = ReadmeUpdater()
    
    # Update report link
    updater.update_recent_reports(notion_url)
    
    # Generate and update heatmap
    try:
        print("📊 Generating indicator heatmap...")
        heatmap_url = generate_indicator_heatmap()
        updater.update_heatmap(heatmap_url)
    except Exception as e:
        print(f"⚠️ Failed to generate heatmap: {e}")
    
    # Save changes
    updater.save()


if __name__ == "__main__":
    main()
