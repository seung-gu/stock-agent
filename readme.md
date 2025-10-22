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
1. market_analysis_agent.py, notion_api, image_service refactor
2. report part workflow refactor
3. test functions


---

## Project Architecture

```
src/
├── config.py                   # Global configuration (language settings)
│
├── agent/                      # AI Agent implementations
│   ├── async_agent.py         # Base class for async agent creation (Template Method pattern)
│   ├── market_analysis_agent.py  # Main orchestration agent
│   ├── liquidity_agent.py     # Treasury yield trend analysis
│   ├── equity_agent.py        # Stock price trend analysis
│   └── notion_agent.py        # Notion upload agent
│
├── services/                   # Business logic services
│   ├── image_service.py       # Image processing & Cloudflare R2 upload
│   └── image_service_test.py  # Unit tests
│
├── adapters/                   # External API integrations
│   ├── notion_api.py          # Notion API client
│   ├── notion_api_test.py     # Unit tests
│   └── notion_integration_test.py  # Integration tests
│
└── utils/                      # Utility functions
    └── charts.py              # Chart generation utilities
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
│     └── EquityTrendAgent (AAPL/SPY/etc)                    │
│                                                             │
│  2. Integrated Report Generation                           │
│     └── market_agent (GPT-4.1-mini)                        │
│                                                             │
│  3. Notion Publishing                                      │
│     └── notion_agent → Image Upload → Notion API          │
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
  • Timeframe-specific Analysis (short/mid/long-term)
  • Actionable Recommendations
  • Markdown Report Generation
  ↓
ReportData {
  short_summary: str
  markdown_report: str  (with sandbox:/ chart links)
  follow_up_questions: list[str]
}
```

#### Phase 3: Notion Publishing
```
notion_agent.post_to_notion(title, content)
  ↓
  1. find_local_images(content)
     • Parse markdown for sandbox:/ links
     • Replace with placeholders: {{IMAGE_PLACEHOLDER:path}}
     ↓
  2. upload_images_to_cloudflare(image_files)
     • Upload each chart to R2 storage
     • Return {local_path: public_url} mapping
     ↓
  3. upload_to_notion(title, processed_content, uploaded_map)
     • create_notion_blocks()
       - Split text into 2000-char chunks
       - Replace placeholders with embed blocks
     • POST to Notion API
       - Initial page with first 100 blocks
       - PATCH remaining blocks (100 per batch)
     ↓
  ✅ Published Notion Page URL
```

---

## Key Components

### AsyncAgent (Base Class)
**Template Method Pattern:**
- `_setup()`: Hook for subclass initialization (ticker_obj, tools)
- `_create_agent()`: Agent creation with tools & instructions
- `run()`: Execute agent with user message

**Subclasses:**
- `TrendResearchBase` → `LiquidityTrendAgent`, `EquityTrendAgent`

### Agent Tools

**Trend Analysis Tools:**
- `analyze_trend(period)`: Calculate price/yield trends (%, absolute changes)
- `plot_trend(period, value_type)`: Generate matplotlib charts → sandbox:/

**Notion Tools:**
- `post_to_notion(title, content)`: Orchestrate image upload & Notion publishing

### External Integrations

**Cloudflare R2:**
- Image storage with public URLs
- Configured via `R2_*` environment variables

**Notion API:**
- Version: `2025-09-03`
- Uses `embed` blocks for external images
- Handles 2000-char text limit & 100-block batch limit

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
