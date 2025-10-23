"""Compare current implementation vs md2notionpage"""
import sys
sys.path.insert(0, '/Users/seung-gu/PycharmProjects/stock-agent/src')

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set NOTION_SECRET for md2notionpage
os.environ['NOTION_SECRET'] = os.environ.get('NOTION_API_KEY', '')

from md2notionpage import md2notionpage
from src.adapters.notion_api import upload_to_notion

# Test markdown with nested lists
test_md = """# Test Document

## Outline Section

1. First numbered item
- Sub bullet one
- Sub bullet two
2. Second numbered item
- Sub bullet three
3. Third numbered item

## Formatting Test

**Bold text** and *italic text* and ***bold italic***

### Code Test
```python
def test():
    return "hello"
```

Inline `code` here.

### Table Test
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |
"""

print("=" * 60)
print("COMPARISON TEST: Current Implementation vs md2notionpage")
print("=" * 60)

parent_page_id = os.environ.get('NOTION_DATABASE_ID')
if parent_page_id and len(parent_page_id) == 32:
    parent_page_id = f"{parent_page_id[:8]}-{parent_page_id[8:12]}-{parent_page_id[12:16]}-{parent_page_id[16:20]}-{parent_page_id[20:]}"

# Test 1: Current implementation
print("\n" + "=" * 60)
print("TEST 1: Current Implementation")
print("=" * 60)

try:
    result = upload_to_notion("Current Implementation Test", test_md, {})
    print(f"✅ Result: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: md2notionpage
print("\n" + "=" * 60)
print("TEST 2: md2notionpage")
print("=" * 60)

try:
    url = md2notionpage(test_md, "md2notionpage Test", parent_page_id)
    print(f"✅ URL: {url}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("COMPARISON COMPLETE")
print("=" * 60)
print("\nCheck both pages in Notion to compare:")
print("1. Nested list handling")
print("2. Formatting preservation")
print("3. Table rendering")
print("4. Code block display")

