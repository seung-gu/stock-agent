### Install uv

curl -LsSf https://astral.sh/uv/install.sh | sh

source $HOME/.local/bin/env

#### Check installation
uv --version


#### Install packages with uv

uv run

#### Set Interpreter

source .venv/bin/activate


### Set Env file

FINNHUB_API_KEY=XXX
GOOGLE_API_KEY=XXX
OPENAI_API_KEY=XXX
POLYGON_API_KEY=XXX
PUSHOVER_TOKEN=XXX
PUSHOVER_USER=XXX
HF_TOKEN=XXX
SENDGRID_API_KEY=XXX
NOTION_API_KEY=XXX
NOTION_DATABASE_ID=XXX
R2_ACCESS_KEY_ID=XXX
R2_SECRET_ACCESS_KEY=XXX
R2_BUCKET_NAME=XXX
R2_ACCOUNT_ID=XXX
R2_PUBLIC_URL=XXX

### Language Settings

Edit `src/config.py` to change report language:
```python
REPORT_LANGUAGE = "English"  # Options: "English" or "Korean"
```

TODO:
1. ~~market_analysis_agent.py refactor~~ ✅
2. ~~report part workflow refactor~~ ✅ (Parent-child structure)
3. ~~language configuration refactor~~ ✅ (Centralized REPORT_LANGUAGE)
4. test functions


---

## Project Architecture

```
src/
├── config.py                   # Global configuration (language settings)
│
├── agent/                      # AI Agent implementations
│   ├── async_agent.py         # Base class for async agent creation (Template Method pattern)
│   ├── trend_agent.py         # Trend analysis base agent with tools
│   ├── liquidity_agent.py    # Treasury yield trend analysis (extends TrendAgent)
│   ├── equity_agent.py        # Stock price trend analysis (extends TrendAgent)
│   ├── market_analysis_agent.py  # Main orchestration agent
│   └── email_agent.py         # Email notification agent
│
├── services/                   # Business logic services
│   ├── image_service.py       # Image processing & Cloudflare R2 upload
│   └── image_service_test.py  # Unit tests
│
├── adapters/                   # External API integrations
│   ├── notion_api.py          # Notion API client (page creation & upload)
│   ├── markdown_to_notion.py  # Markdown parser → Notion blocks converter
│   ├── report_builder.py      # Parent-child page structure builder
│   ├── notion_api_test.py     # Unit tests
│   ├── markdown_to_notion_test.py  # Unit tests
│   └── report_builder_test.py # Integration tests
│
├── utils/                      # Utility functions
│   └── charts.py              # Chart generation utilities
│
└── dep/                        # Deprecated/legacy code
    ├── agent.py
    └── market_agent.py
```

---

## Program Workflow

### 1. Main Orchestration (`MarketResearchManager`)

```
┌─────────────────────────────────────────────────────────────┐
│                  MarketResearchManager                      │
│                                                             │
│  1. Parallel Analysis                                       │
│     ├── LiquidityTrendAgent (^TNX)                         │
│     │   • Trend analysis (5d, 1mo, 6mo)                    │
│     │   • Chart generation                                  │
│     └── EquityTrendAgent (AAPL/SPY/etc)                    │
│         • Trend analysis (5d, 1mo, 6mo)                    │
│         • Chart generation                                  │
│                                                             │
│  2. Report Synthesis (market_agent)                        │
│     • Strategic insights generation                         │
│     • Child page titles generation (in configured language)│
│     • ReportData schema output                             │
│                                                             │
│  3. Notion Publishing (Parent-Child Structure)           │
│     • upload_report_with_children()                        │
│     • Image processing (shared across all pages)           │
│     • Child pages: Liquidity | Equity | Conclusion        │
└─────────────────────────────────────────────────────────────┘
```

### 2. Detailed Flow

#### Phase 1: Data Collection & Analysis
```
User Request → MarketResearchManager.run(equity_ticker, liquidity_ticker)
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
LiquidityTrendAgent              EquityTrendAgent
  • 5d/1mo/6mo trend analysis     • 5d/1mo/6mo trend analysis
  • Chart generation (sandbox:/)  • Chart generation (sandbox:/)
  • Analysis report generation    • Analysis report generation
        ↓                               ↓
        └───────────────┬───────────────┘
                        ↓
            Combined Analysis Results
```

#### Phase 2: Report Synthesis
```
market_agent (GPT-4.1-mini)
  ↓
  • Correlation Analysis (liquidity vs equity)
  • Strategic Insights & Recommendations
  • Agent-generated Page Titles (in configured language)
  • Markdown Report Generation
  ↓
ReportData {
  title: str                      # Main report title
  date: str                       # Report date
  short_summary: str              # Executive summary
  main_report: str                # Full conclusion & insights
  child_page_titles: list[str]    # Titles for child pages [liquidity, equity, conclusion]
}
```

#### Phase 3: Notion Publishing (Parent-Child Structure)
```
upload_report_with_children(title, date, summary, child_pages, uploaded_map)
  ↓
  1. Create Parent Page
     • Title: Agent-generated report title
     • Content: Report date + executive summary
     ↓
  2. Process Images (for all pages)
     • find_local_images(all_content)
       - Parse markdown for sandbox:/ links
       - Replace with placeholders: {{IMAGE_PLACEHOLDER:path}}
     • upload_images_to_cloudflare(image_files)
       - Upload to R2 storage
       - Return {local_path: public_url} mapping
     ↓
  3. Create Child Pages
     For each child_page: (title, content)
       • MarkdownToNotionParser.parse(content)
         - Parse markdown: headings, lists, tables, code blocks
         - Convert formatting: **bold**, *italic*, `code`
         - Handle nested lists (numbered + bullets)
         - Replace placeholders with embed blocks
         - Split text into 2000-char chunks
       • create_child_page(parent_id, title, content, uploaded_map)
         - POST to Notion API with parent_page_id
         - PATCH remaining blocks (100 per batch)
     ↓
  3 Child Pages:
     • {child_page_titles[0]}: Liquidity Analysis (with charts)
     • {child_page_titles[1]}: Equity Analysis (with charts)
     • {child_page_titles[2]}: Conclusion & Insights
     ↓
  ✅ Published Notion Page with Children
```

---

## Key Components

### Language Configuration
**Set in `src/config.py`:**
```python
REPORT_LANGUAGE = "Korean"  # or "English"
```
- All agent outputs adapt to this setting
- Page titles, summaries, and reports generated in configured language
- No hardcoded language strings in the codebase

### AsyncAgent (Base Class)
**Template Method Pattern:**
- `_setup()`: Hook for subclass initialization (ticker_obj, tools)
- `_create_agent()`: Agent creation with tools & instructions
- `run()`: Execute agent with user message

**Subclasses:**
- `TrendAgent` → `LiquidityTrendAgent`, `EquityTrendAgent`

### Agent Tools

**Trend Analysis Tools:**
- `analyze_trend(period)`: Calculate price/yield trends (%, absolute changes)
- `plot_trend(period, value_type)`: Generate matplotlib charts → sandbox:/
- `get_value_unit()`: Determine chart unit type (USD, PERCENTAGE, INDEX, etc.)

### Report Builder
**`upload_report_with_children()`:**
- Creates parent page with title, date, and summary
- Generates child pages with agent-provided titles
- Processes images once for all pages (shared uploaded_map)
- Returns parent page ID and URL

### External Integrations

**Cloudflare R2:**
- Image storage with public URLs
- Configured via `R2_*` environment variables

**Notion API:**
- Version: `2025-09-03`
- Uses `embed` blocks for external images
- **MarkdownToNotionParser**:
  - Class-based architecture for parsing markdown
  - Supports: headings, lists (nested), tables, code blocks
  - Handles: bold, italic, bold-italic, inline code
  - Respects Notion limits: 2000 chars per block, 100 blocks per page

---

## Testing

Run all tests:
```bash
python -m unittest discover src -p "*_test.py"
```

Or use **Test Explorer** in VS Code/Cursor (configured in `.vscode/settings.json`)

---

## Example Report

https://seunggu-kang.notion.site/MSFT-29362b45fc8081659125cfbb6df03307
https://seunggu-kang.notion.site/Comprehensive-Market-Analysis-Report-Apple-Inc-AAPL-with-Liquidity-Conditions-29462b45fc8081779469d970d06f5ce5
