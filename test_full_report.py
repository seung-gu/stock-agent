"""Test md2notionpage with full market analysis report"""
import sys
sys.path.insert(0, '/Users/seung-gu/PycharmProjects/stock-agent/src')

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Set NOTION_SECRET from NOTION_API_KEY before importing md2notionpage
os.environ['NOTION_SECRET'] = os.environ.get('NOTION_API_KEY', '')

from md2notionpage import md2notionpage

# Full market analysis report sample
full_report = """# Market Analysis Report

## Executive Summary

The market shows mixed signals with liquidity conditions stabilizing while equity markets continue to show strength. This analysis examines the relationship between Treasury yields (^TNX) and Apple stock (AAPL) across multiple timeframes.

## Liquidity Analysis (Treasury Yields: ^TNX)

### Short-term (5 days)
The 5-day trend shows **increased volatility** in Treasury yields, indicating uncertainty in the short-term interest rate outlook. Yield movements have been relatively contained within a narrow range.

### Medium-term (1 month)
Over the past month, Treasury yields have shown a *moderate upward trend*, suggesting improving economic confidence. The yield curve has steepened slightly, which typically indicates expectations of future growth.

### Long-term (6 months)
The 6-month analysis reveals a **significant recovery** from previous lows. Long-term yields have normalized, reflecting the Federal Reserve's ongoing monetary policy adjustments.

## Equity Analysis (AAPL Stock Price)

### Short-term (5 days)
AAPL has demonstrated **strong momentum** in the short term, with consistent upward price movement. Volume patterns suggest genuine buying interest rather than speculative trading.

### Medium-term (1 month)
The medium-term trend shows *robust performance* with Apple stock outperforming broader market indices. The company's fundamentals remain strong, supporting the price appreciation.

### Long-term (6 months)
Long-term analysis indicates **sustained growth** trajectory. Apple's strategic initiatives in services and new product categories have provided solid foundation for continued value creation.

## Correlation and Integrated Insights

### Alignment and divergence overview
The correlation between Treasury yields and Apple stock has been **notably positive** in recent periods, suggesting that improving economic conditions benefit both asset classes simultaneously.

### Timeframe-specific correlation
- **Short-term**: Positive correlation (0.65)
- **Medium-term**: Moderate correlation (0.45)
- **Long-term**: Weaker correlation (0.30)

## Actionable Recommendations

### Investment outlook
Based on current analysis, the outlook is **cautiously optimistic**. Both liquidity conditions and equity performance suggest a favorable environment for continued market strength.

### Risks and monitoring points
Key risks to monitor include:
- Potential Federal Reserve policy shifts
- Geopolitical tensions affecting global markets
- Supply chain disruptions in tech sector
- Energy price volatility

### Entry and exit timing
For investors looking to add exposure:
- **Entry**: Consider gradual accumulation on any pullbacks below key support levels
- **Exit**: Monitor resistance levels and consider partial profit-taking on significant rallies

## Conclusion

The integrated analysis suggests a **balanced market environment** with opportunities for selective investment. Both liquidity indicators and equity fundamentals support continued market participation, though vigilance regarding risk factors remains essential.

### Key Takeaways
1. Treasury yields show healthy normalization trend
2. Apple stock demonstrates strong fundamental support
3. Positive correlation indicates synchronized economic improvement
4. Risk management remains critical in current environment
"""

# Get credentials
parent_page_id = os.environ.get('NOTION_PARENT_PAGE_ID') or os.environ.get('NOTION_DATABASE_ID')

# Format parent_page_id (add hyphens if needed)
if parent_page_id and len(parent_page_id) == 32:
    parent_page_id = f"{parent_page_id[:8]}-{parent_page_id[8:12]}-{parent_page_id[12:16]}-{parent_page_id[16:20]}-{parent_page_id[20:]}"

print("=" * 60)
print("TESTING MD2NOTIONPAGE WITH FULL REPORT")
print("=" * 60)
print(f"DEBUG: NOTION_SECRET set: {bool(os.environ.get('NOTION_SECRET'))}")
print(f"DEBUG: Parent ID: {parent_page_id}")
print(f"Report length: {len(full_report)} characters")

if not os.environ.get('NOTION_SECRET') or not parent_page_id:
    print("❌ NOTION_SECRET or NOTION_PARENT_PAGE_ID not found")
    sys.exit(1)

title = "Full Market Analysis Report - md2notionpage Test"

try:
    print(f"\n📤 Creating full report page...")
    print(f"   Title: {title}")
    print(f"   Parent ID: {parent_page_id}")
    
    url = md2notionpage(full_report, title, parent_page_id)
    
    print(f"\n✅ Success!")
    print(f"🔗 Page URL: {url}")
    print(f"\nCheck Notion to see if nested lists, formatting, and structure are preserved correctly.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

