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
FRED_API_KEY=XXX

### Language Settings

Edit `src/config.py` to change report language:
```python
REPORT_LANGUAGE = "English"  # Options: "English" or "Korean"
```

TODO:
1. ~~market_analysis_agent.py refactor~~ ✅
2. ~~report part workflow refactor~~ ✅ (Parent-child structure)
3. ~~language configuration refactor~~ ✅ (Centralized REPORT_LANGUAGE)
4. ~~unified data source system~~ ✅ (Registry pattern with auto-detection)
5. ~~NFCI integration~~ ✅ (via FREDSource)
6. ~~markdown parsing improvements~~ ✅ (3-level nested lists, proper indentation)
7. ~~test functions~~ ✅ (18 comprehensive tests with API limitations handling)
8. ~~create an entry point~~ ✅ (run_market_report.py)
9. ~~market_analysis_agent refactor~~ ✅ (MarketReportAgent, direct agent connection)
10. ~~markdown_to_notion refactor~~ ✅ (recursive heading and bullet point with API limitations)
11. ~~TNX agent analysis accuracy~~ ✅
12. ~~AnalysisReport type system~~ ✅ (Structured output types)
13. ~~FRED API error handling~~ ✅ (Mock data fallback)
14. ~~SMA (Simple Moving Averages) implementation~~ ✅ (5/20/200-day SMAs with candlestick charts)
15. ~~Unit testing with Mock API~~ ✅ (17 tests, no real API calls)


---

## Project Architecture

```
src/
├── config.py                   # Global configuration (language settings)
│
├── agent/                      # AI Agent implementations (organized by role)
│   ├── base/                  # 🏗️ Base abstract classes
│   │   ├── __init__.py       # Exports: AsyncAgent, OrchestratorAgent, TrendAgent
│   │   ├── async_agent.py    # Base class for async agents (Template Method pattern)
│   │   ├── orchestrator_agent.py  # Base class for orchestrators (parallel execution)
│   │   └── trend_agent.py    # Base class for trend analysis with unified tools
│   │
│   ├── trend/                 # 📈 Trend analysis agents
│   │   ├── __init__.py       # Exports: TNXAgent, NFCIAgent, DXAgent, EquityTrendAgent
│   │   ├── tnx_agent.py      # Treasury yield (^TNX) analysis
│   │   ├── nfci_agent.py     # NFCI (National Financial Conditions Index) analysis
│   │   ├── dx_agent.py       # Dollar Index (DX=F) analysis
│   │   └── equity_trend_agent.py  # Stock price trend analysis
│   │
│   ├── orchestrator/          # 🎭 Orchestrator agents (combine multiple agents)
│   │   ├── __init__.py       # Exports: LiquidityAgent, MarketReportAgent
│   │   ├── liquidity_agent.py     # Liquidity orchestrator (TNX + NFCI + DX)
│   │   └── market_report_agent.py  # Main report agent (Liquidity + Equity)
│   │
│   └── types/                 # 📋 Type definitions
│       ├── __init__.py       # Package initialization
│       └── analysis_report.py  # AnalysisReport Pydantic model
│   │
│   └── email_agent.py         # 📧 Email notification agent
│
├── services/                   # Business logic services
│   ├── image_service.py       # Image processing & Cloudflare R2 upload
│   └── image_service_test.py  # Unit tests
│
├── adapters/                   # External API integrations
│   ├── notion_api.py          # Notion API client (page creation & upload)
│   ├── markdown_to_notion.py  # Advanced markdown parser → Notion blocks converter
│   │                          # • 3-level nested lists (numbered → bulleted → bulleted)
│   │                          # • Pythonic recursive parsing
│   │                          # • Proper indentation handling
│   │                          # • Notion API limitations handling (h4-h6, numbered lists)
│   ├── report_builder.py      # Parent-child page structure builder
│   ├── notion_api_test.py     # Unit tests
│   ├── markdown_to_notion_test.py  # Unit tests (18 tests, all passing)
│   └── report_builder_test.py # Integration tests
│
├── utils/                      # Utility functions
│   ├── charts.py              # Unified chart generation (yfinance & FRED)
│   │                          # • Candlestick charts with SMA overlays
│   │                          # • 5/20/200-day Simple Moving Averages
│   │                          # • Weekend gap removal for continuous display
│   ├── data_sources.py        # Data source registry (YFinanceSource, FREDSource)
│   │                          # • Automatic SMA calculation (5/20/200-day)
│   │                          # • Extended data fetching for SMA 200
│   ├── data_sources_test.py   # Unit tests (10 tests, Mock API)
│   └── charts_test.py         # Unit tests (7 tests, Mock API)
│
└── dep/                        # Deprecated/legacy code
    ├── agent.py
    └── market_agent.py
```

---

## Program Workflow

### 1. Main Orchestration (`run_market_report.py`)

```
┌─────────────────────────────────────────────────────────────┐
│                    run_market_report.py                     │
│                                                             │
│  1. Direct Agent Execution                                  │
│     ├── MarketReportAgent (Orchestrator)                    │
│     │   ├── LiquidityAgent (TNX + NFCI + DX)                │
│     │   └── EquityTrendAgent (Stock Analysis + SMA)         │
│     │       • 4-period analysis (5d/1mo/6mo/1y)             │
│     │       • Candlestick charts with moving averages       │
│     │       • Technical indicators (SMA 5/20/200)           │
│     │                                                       │
│     └── Synthesis Agent (Combined Analysis)                 │
│                                                             │
│  2. Image Processing & Notion Publishing                    │
│     • find_local_images() - Parse chart links               │
│     • upload_images_to_cloudflare() - R2 storage            │
│     • upload_report_with_children() - Parent-child pages    │
│     • Child pages: Liquidity | Equity | Synthesis           │
│     • Enhanced equity analysis with moving averages         │
└─────────────────────────────────────────────────────────────┘
```

### 2. Detailed Flow

#### Phase 1: Data Collection & Analysis
```
User Request → run_market_report()
                        ↓
        ┌───────────────┴───────────────┐
        ↓                               ↓
  LiquidityAgent                  EquityTrendAgent
  (TNX + NFCI + DX)              (Stock Analysis)
        ↓                               ↓
  ┌─────┴─────┐                   • get_yf_data(NVDA, 5d/1mo/6mo/1y)
  ↓           ↓                   • create_yfinance_chart() for 1mo, 1y only
TNXAgent   NFCIAgent              • Candlestick charts with SMA overlays:
  ↓           ↓                     - 1mo: SMA 5, 20 (short-term trends)
  ↓           ↓                     - 1y: SMA 5, 20, 200 (comprehensive analysis)
  ↓           ↓                   • Technical analysis with moving averages
• get_yf    • get_fred
  _data       _data
• create    • create
  _yf_        _fred_
  chart       chart
  ↓           ↓
  └─────┬─────┘
        ↓
  Synthesis
  (Combined
   Liquidity)
        ↓
        └───────────────┬───────────────┘
                        ↓
            Combined Analysis Results
```

#### Phase 2: Report Synthesis
```
Synthesis Agent (GPT-4.1-mini)
  ↓
  • Correlation Analysis (liquidity vs equity)
  • Strategic Insights & Recommendations
  • AnalysisReport Generation
  ↓
AnalysisReport {
  title: str                      # Specific, descriptive title
  summary: str                    # Executive summary
  content: str                    # Detailed analysis content
}
```

#### Phase 2: Image Processing & Notion Publishing
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
       - Upload to R2 storage (candlestick charts + SMA overlays)
       - Return {local_path: public_url} mapping
     ↓
  3. Create Child Pages
     For each child_page: (title, content)
       • MarkdownToNotionParser.parse(content)
         - Parse markdown: headings, lists, tables, code blocks
         - Convert formatting: **bold**, *italic*, `code`
         - Handle 3-level nested lists (numbered → bulleted → bulleted)
         - Smart indentation detection and hierarchy recognition
         - Replace placeholders with embed blocks
         - Split text into 2000-char chunks
       • create_child_page(parent_id, title, content, uploaded_map)
         - POST to Notion API with parent_page_id
         - PATCH remaining blocks (100 per batch)
     ↓
  3 Child Pages:
     • Liquidity Analysis (with charts)
     • Equity Analysis (with candlestick charts + SMA overlays)  
     • Market Strategy Summary (with synthesis)
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

### Agent Architecture

#### Base Classes (`agent/base/`)

**AsyncAgent (Template Method Pattern):**
- `_setup()`: Hook for subclass initialization
- `_create_agent()`: Agent creation with tools & instructions
- `run()`: Execute agent with user message

**OrchestratorAgent (extends AsyncAgent):**
- `sub_agents`: List of agents to orchestrate
- `synthesis_agent`: Agent for combining results
- `run()`: Parallel execution + synthesis
- `_create_synthesis_prompt()`: Abstract method for custom synthesis

**TrendAgent (extends AsyncAgent):**
- Unified tools: `get_yf_data`, `get_fred_data`, `create_yfinance_chart`, `create_fred_chart`
- Context-aware instructions
- Extensible for any ticker/indicator

#### Concrete Implementations

**Trend Agents (`agent/trend/`):**
- `TNXAgent`: Treasury yield analysis (^TNX via yfinance)
- `NFCIAgent`: Financial conditions analysis (NFCI via FRED)
- `DXAgent`: Dollar Index analysis (DX=F via yfinance)
- `EquityTrendAgent`: Stock price analysis (NVDA/SPY/etc via yfinance)

**Orchestrators (`agent/orchestrator/`):**
- `LiquidityAgent`: Orchestrates TNXAgent + NFCIAgent + DXAgent
- `MarketReportAgent`: Orchestrates LiquidityAgent + EquityTrendAgent

### Unified Data Source System

**`data_sources.py` - Extensible Architecture:**
- `DataSource` (ABC): Base class for all data sources
  - `fetch_data()`: Retrieve data
  - `create_chart()`: Generate visualizations
  - `get_analysis()`: Extract metrics

**Implementations:**
- `YFinanceSource`: Stocks, ETFs, treasuries (^TNX, AAPL, SPY)
  - Automatic SMA calculation (5/20/200-day)
  - Extended data fetching for SMA 200 (period + 280 days)
  - Timezone normalization for safe date comparisons
- `FREDSource`: Economic indicators (NFCI, DFF, T10Y2Y)
  - Lazy initialization for FRED API key
  - Indicator-specific configurations

**Explicit Source Selection:**
```python
get_data_source("yfinance")  # → YFinanceSource
get_data_source("fred")      # → FREDSource
```

**Agent Tools:**
- `get_yf_data(symbol, period)`: Fetch data from yfinance
- `get_fred_data(symbol, period)`: Fetch data from FRED
- `create_yfinance_chart(symbol, period)`: Generate yfinance chart
- `create_fred_chart(symbol, period)`: Generate FRED chart

**Unified Charting (`charts.py`):**
- `create_chart()`: Universal chart generator
  - Handles both DataFrame (yfinance) and Series (FRED)
  - Automatic baseline detection for FRED indicators
  - Consistent styling across all chart types
- **Candlestick Charts with SMA Overlays:**
  - OHLC (Open, High, Low, Close) candlestick visualization
  - 5-day, 20-day, 200-day Simple Moving Averages
  - Conditional SMA display based on chart period:
    * No SMAs for 5-day charts
    * SMA 5, 20 for 1mo, 3mo, 6mo periods
    * SMA 5, 20, 200 for 1y+ periods
  - Weekend/holiday gap removal for continuous display
  - Distinct colors and line weights for each SMA

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
- **MarkdownToNotionParser** (Advanced Features):
  - **3-Level Nested Lists**: numbered → bulleted → bulleted
  - **Pythonic Recursive Parsing**: Clean, maintainable code
  - **Smart Indentation Detection**: Automatic hierarchy recognition
  - **Notion API Compatibility**: `paragraph` + `children` structure
  - **Supports**: headings (h1-h6), tables, code blocks, formatting
  - **Handles**: bold, italic, bold-italic, inline code
  - **Respects Notion limits**: 2000 chars per block, 100 blocks per page
  - **Test Coverage**: 30 comprehensive tests, all passing

---

## Recent Improvements

### SMA (Simple Moving Averages) Implementation (v3.0)

**Technical Analysis Enhancement:**
- **5-day, 20-day, 200-day Simple Moving Averages** automatically calculated
- **Candlestick Charts** with SMA overlays for professional stock analysis
- **Conditional SMA Display** based on chart period:
  * 5-day charts: No SMAs (too short for meaningful analysis)
  * 1mo, 3mo, 6mo: SMA 5, 20 (short to medium-term trends)
  * 1y+: SMA 5, 20, 200 (comprehensive trend analysis)
- **Weekend Gap Removal** for continuous candlestick display
- **Extended Data Fetching** (period + 280 days) to ensure sufficient data for SMA 200

**Chart Features:**
- OHLC (Open, High, Low, Close) candlestick visualization
- Distinct colors and line weights for each SMA
- Professional financial chart styling
- Automatic timezone handling for accurate date comparisons

**Agent Integration:**
- SMA data included in trend analysis output
- Current price vs SMA comparisons
- Enhanced technical analysis capabilities

### Advanced Markdown Parsing (v2.0)

**3-Level Nested List Support:**
```markdown
1. 주요 패턴 및 트렌드
   - TNX (10년 만기 국채 수익률)
     - 단기 및 중기적 하락
     - 6개월 기준으로도 큰 하락
   - NFCI (국가 금융 조건 지수)
     - 느슨한 금융 조건
```

**Notion Output:**
```
1. 주요 패턴 및 트렌드
   • TNX (10년 만기 국채 수익률)
      • 단기 및 중기적 하락
      • 6개월 기준으로도 큰 하락
   • NFCI (국가 금융 조건 지수)
      • 느슨한 금융 조건
```

**Key Features:**
- ✅ **Smart Hierarchy Detection**: Automatic recognition of nested structures
- ✅ **Pythonic Code**: Clean, maintainable recursive parsing
- ✅ **Notion API Compatibility**: Proper `paragraph` + `children` structure
- ✅ **Test Coverage**: 30 comprehensive tests, all passing
- ✅ **Performance**: Efficient parsing without infinite loops

---

## Usage Examples

### Import Agents

```python
# Import from organized structure
from src.agent.base import AsyncAgent, OrchestratorAgent, TrendAgent
from src.agent.trend import TNXAgent, NFCIAgent, DXAgent, EquityTrendAgent
from src.agent.orchestrator import LiquidityAgent, MarketReportAgent

# Initialize agents
tnx_agent = TNXAgent()                      # ^TNX analysis
nfci_agent = NFCIAgent()                    # NFCI analysis
dx_agent = DXAgent()                        # DX=F analysis
equity_agent = EquityTrendAgent("NVDA")     # NVDA analysis
liquidity_agent = LiquidityAgent()          # TNX + NFCI + DX orchestrator
manager = MarketReportAgent()               # Full analysis orchestrator
```

### Run Full Market Analysis

```python
import asyncio
from src.run_market_report import run_market_report

async def main():
    # Run full analysis and post to Notion
    result = await run_market_report()
    
    print(f"✅ Report published: {result['url']}")

asyncio.run(main())
```

---

## Testing

**Run all tests:**
```bash
python -m unittest discover src -p "*_test.py"
```

**Run tests with Notion upload (creates actual pages):**
```bash
# Method 1: Set environment variable inline
TEST_MODE=true python -m unittest discover src -p "*_test.py"

# Method 2: Set environment variable in shell
export TEST_MODE=true
python -m unittest discover src -p "*_test.py"
export TEST_MODE=false  # Turn off after testing
```

**Test Coverage:**
- ✅ **MarkdownToNotionParser**: 17 tests (nested lists, headings, tables, code blocks, Notion upload verification)
- ✅ **NotionAPI**: 9 tests (page creation, child pages)
- ✅ **ReportBuilder**: 3 tests (end-to-end workflow tests)
- ✅ **ImageService**: 4 tests (Cloudflare R2 upload tests)
- ✅ **DataSources**: 10 tests (yfinance/FRED with Mock API, SMA calculations)
- ✅ **Charts**: 7 tests (candlestick charts, SMA overlays, weekend gap removal)
- ✅ **Total**: 50 comprehensive tests
- ⚠️ **Notion Upload Test**: Only runs when `TEST_MODE=true` (prevents creating pages during normal testing)
- 🚫 **No Real API Calls**: All tests use Mock data for fast, reliable execution

**Test Explorer**: Use VS Code/Cursor Test Explorer (configured in `.vscode/settings.json`)

**Recent Test Results:**
```
# Data Sources Tests
Ran 10 tests in 0.013s
OK

# Charts Tests  
Ran 7 tests in 0.584s
OK

# All Tests Combined
Ran 50 tests in 3.2s
OK
✅ All tests passed
```

---

## Example Report

https://seunggu-kang.notion.site/MSFT-29362b45fc8081659125cfbb6df03307
https://seunggu-kang.notion.site/Comprehensive-Market-Analysis-Report-Apple-Inc-AAPL-with-Liquidity-Conditions-29462b45fc8081779469d970d06f5ce5
