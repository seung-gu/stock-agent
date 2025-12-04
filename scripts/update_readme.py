#!/usr/bin/env python3
"""Update README with latest report link"""

import sys
import re
from datetime import datetime

def update_readme(notion_url: str):
    """
    Update README.md with the latest report link.
    
    Args:
        notion_url: Notion page URL from the generated report
    """
    readme_path = "readme.md"
    
    # Read current README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Generate date string
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Create new link entry
    new_entry = f"- [{date_str}]({notion_url})"
    
    # Find the "Recent Reports" section and update
    pattern = r'(### Recent Reports.*?\n)(.*?)(\n###|\n---|\Z)'
    
    def replace_section(match):
        header = match.group(1)
        body = match.group(2)
        next_section = match.group(3)
        
        # Split existing links
        lines = body.strip().split('\n')
        links = [line for line in lines if line.strip().startswith('-') or line.strip().startswith('**')]
        
        # Remove existing entry with same date
        links = [link for link in links if f"[{date_str}]" not in link]
        
        # Add new entry at the top
        links.insert(0, new_entry)
        
        # Keep only last 10 reports
        links = links[:10]
        
        return header + '\n'.join(links) + '\n' + next_section
    
    # Update README
    updated_content = re.sub(pattern, replace_section, content, flags=re.DOTALL)
    
    # Write back
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ README updated with report: {notion_url}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python update_readme.py <notion_url>")
        sys.exit(1)
    
    notion_url = sys.argv[1]
    update_readme(notion_url)