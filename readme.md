
## Example Report
English ver:
https://seunggu-kang.notion.site/Comprehensive-Market-Insights-and-Synthesis-Report-October-2025-Week-5-Year-2025-29d62b45fc808134ae62e76a2dc06ccf?pvs=74

Korean ver:
https://seunggu-kang.notion.site/2025-10-29d62b45fc808174aeb6f355f8eaab1d?pvs=74

---
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
7. ~~test functions~~ ✅ (51 comprehensive tests with API limitations handling)
8. ~~create an entry point~~ ✅ (run_market_report.py)
9. ~~market_analysis_agent refactor~~ ✅ (MarketReportAgent, direct agent connection)
10. ~~markdown_to_notion refactor~~ ✅ (recursive heading and bullet point with API limitations)
11. ~~TNX agent analysis accuracy~~ ✅
12. ~~AnalysisReport type system~~ ✅ (Structured output types)
13. ~~FRED API error handling~~ ✅ (Mock data fallback)
14. ~~SMA (Simple Moving Averages) implementation~~ ✅ (5/20/200-day SMAs with candlestick charts)
15. ~~Unit testing with Mock API~~ ✅ (51 tests, no real API calls)
16. API Verificator (Only return values when tool gets 200 request status)
17. Table and charts correspond to the requirements
18. ~~Technical Indicator System Refactor~~ ✅ (TechnicalAnalyzer fluent API, chart separation, Equity disparity support)
19. ~~SMA(200) Chart Cut-off Fix~~ ✅ (Extended buffer with BDay offset, pre-compute SMAs, smart slicing)
20. ~~Modular Agent Tools Architecture~~ ✅ (9 independent function_tools, complete layer separation, agent autonomy)


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
│   │   └── trend_agent.py    # Base class for trend analysis (simplified, tool-agnostic)
│   │
│   ├── tools/                 # 🛠️ Modular function tools (v6.0 - Dynamic Thresholds)
│   │   └── agent_tools.py    # 7 independent @function_tool for agents
│   │                         # • fetch_data, analyze_OHLCV_data, generate_OHLCV_chart
│   │                         # • analyze_SMA_data, analyze_disparity_data, analyze_RSI_data
│   │                         # • generate_disparity_chart, generate_RSI_chart
│   │                         # • Dynamic overbought/oversold thresholds (80th/10th percentile)
│   │                         # • Cache-based, complete layer separation
│   │
│   ├── trend/                 # 📈 Trend analysis agents
│   │   ├── __init__.py       # Exports: TNXAgent, NFCIAgent, DXAgent, EquityTrendAgent
│   │   ├── tnx_agent.py      # Treasury yield (^TNX) analysis
│   │   ├── nfci_agent.py     # NFCI (National Financial Conditions Index) analysis
│   │   ├── dx_agent.py       # Dollar Index (DX=F) analysis
│   │   └── equity_trend_agent.py  # Stock price trend analysis
│   │
│   ├── orchestrator/          # 🎭 Orchestrator agents (combine multiple agents)
│   │   ├── __init__.py       # Exports: LiquidityAgent, BroadIndexAgent, MarketReportAgent
│   │   ├── liquidity_agent.py     # Liquidity orchestrator (TNX + NFCI + DX)
│   │   ├── broad_index_agent.py   # Broad index orchestrator (^GSPC + ^IXIC + ^DJI)
│   │   └── market_report_agent.py  # Main report agent (Liquidity + BroadIndex + Equity)
│   │
│   └── types/                 # 📋 Type definitions
│       ├── __init__.py       # Package initialization
│       └── analysis_report.py  # AnalysisReport Pydantic model
│   │
│   └── email_agent.py         # 📧 Email notification agent
│
├── utils/                      # Utility modules
│   ├── charts.py              # Chart generation system
│   │   ├── create_yfinance_chart()  # Candlestick with SMA overlays
│   │   ├── create_fred_chart()      # FRED line chart with baseline
│   │   └── create_line_chart()      # Generic line chart (disparity, RSI, etc.)
│   ├── data_sources.py        # Unified data source system
│   │                          # • YFinanceSource, FREDSource
│   │                          # • Smart caching (fetch once, slice multiple)
│   │                          # • Raw OHLCV data only (no calculations)
│   ├── technical_indicators.py  # Technical analysis pure functions
│   │                          # • calculate_sma, calculate_disparity, calculate_rsi, calculate_macd
│   │                          # • Used by agent_tools.py
│   │                          # • No agent coupling (pure calculation)
│   ├── data_sources_test.py   # Unit tests (10 tests, Mock API)
│   └── charts_test.py         # Unit tests (7 tests, Mock API)
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

DXAgent
  ↓
• get_yf_data(DX=F, 5d/1mo/6mo/1y)
• create_yfinance_chart() for 1y only
• Currency index analysis (Dollar strength/weakness)rt
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
- Tool-agnostic base class (simplified)
- Context-aware instructions with `label` and `description` parameters
- `label`: Human-readable name (e.g., "S&P 500" for "^GSPC")
- `description`: Brief asset description (optional)
- Extensible for any ticker/indicator
- Tools selected by subclasses from `agent_tools.py`

#### Concrete Implementations

**Trend Agents (`agent/trend/`):**
- `TNXAgent`: Treasury yield analysis (^TNX via yfinance)
- `NFCIAgent`: Financial conditions analysis (NFCI via FRED)
- `DXAgent`: Dollar Index analysis (DX=F via yfinance)
- `EquityTrendAgent`: Stock price analysis (NVDA/SPY/etc via yfinance)

**Orchestrators (`agent/orchestrator/`):**
- `LiquidityAgent`: Orchestrates TNXAgent + NFCIAgent + DXAgent
- `BroadIndexAgent`: Orchestrates S&P 500 + Nasdaq + Dow Jones analysis
- `MarketReportAgent`: Orchestrates LiquidityAgent + BroadIndexAgent + EquityTrendAgent

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

**Modular Agent Tools (`agent/tools/agent_tools.py`):**

**Data Layer:**
- `fetch_data(source, symbol, period)`: Fetch and cache data from yfinance/FRED

**Analysis Layer:**
- `analyze_OHLCV_data(source, symbol, period)`: Extract OHLCV metrics from cache
- `analyze_SMA_data(symbol, period, windows)`: Calculate SMA indicators
- `analyze_disparity_data(symbol, period, window)`: Calculate disparity with dynamic thresholds (80th/10th percentile)
- `analyze_RSI_data(symbol, period, window)`: Calculate RSI with dynamic thresholds (80th/10th percentile)

**Chart Layer:**
- `generate_OHLCV_chart(source, symbol, period)`: Generate candlestick/line chart
- `generate_disparity_chart(symbol, period, window)`: Generate disparity chart with dynamic threshold lines
- `generate_RSI_chart(symbol, period, window)`: Generate RSI chart with dynamic threshold lines

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

### Dynamic Thresholds & Agent Enhancements (v6.0)

**Date: October 31, 2025**

**Major Updates:**

**1. BroadIndexAgent - New Orchestrator:**
- Dedicated orchestrator for major US market indices
- Combines S&P 500 (^GSPC), Nasdaq Composite (^IXIC), Dow Jones (^DJI)
- Provides comprehensive broad market analysis
- Integrated into `MarketReportAgent` workflow

**2. TrendAgent Label & Description:**
- Added `label` parameter for human-readable asset names
  - Example: `label="S&P 500"` instead of displaying `^GSPC`
- Added `description` parameter for brief asset descriptions
  - Example: `description="Gold-tracking ETF"` for IAU
- Improves LLM context and report readability
- Applied to all trend agents (TNX, NFCI, DX, Equity, BroadIndex)

**3. Dynamic Overbought/Oversold Thresholds:**
- **RSI Analysis**: Now uses 80th/10th percentile instead of fixed 70/30
  - `analyze_RSI_data()`: Returns current RSI with dynamic thresholds
  - `generate_RSI_chart()`: Visualizes thresholds with shaded regions
- **Disparity Analysis**: Now uses 80th/10th percentile instead of fixed ±20%
  - `analyze_disparity_data()`: Returns current disparity with dynamic thresholds
  - `generate_disparity_chart()`: Visualizes thresholds with shaded regions
- **Benefits**: Adapts to each asset's historical volatility patterns
- **Chart Updates**: `create_line_chart()` now supports `threshold_upper`/`threshold_lower`

**4. Code Cleanup:**
- Removed MACD-related functions (`analyze_MACD_data`, `generate_MACD_chart`)
- Removed `calculate_macd` from technical indicators
- Simplified tool count from 9 to 7 focused tools
- Maintained `baseline` parameter for FRED charts compatibility

**Agent Tool Updates:**
```python
# analyze_RSI_data output (NEW)
"RSI(14): 65.32 [Overbought>72.1, Oversold<31.5]"

# analyze_disparity_data output (NEW)
"Disparity(200): 15.23% [Overbought>18.5%, Oversold<-12.3%]"

# EquityTrendAgent example with label & description
EquityTrendAgent(
    "IAU", 
    label="iShares Gold Trust",
    description="Gold-tracking ETF"
)
```

**Files Modified:**
- `src/agent/base/trend_agent.py`: Added `label`, `description` parameters
- `src/agent/trend/equity_agent.py`: Updated to accept and pass new parameters
- `src/agent/trend/tnx_agent.py`, `nfci_agent.py`, `dx_agent.py`: Applied labels
- `src/agent/orchestrator/broad_index_agent.py`: NEW orchestrator
- `src/agent/orchestrator/market_report_agent.py`: Integrated BroadIndexAgent
- `src/agent/tools/agent_tools.py`: Dynamic thresholds, removed MACD
- `src/utils/charts.py`: Enhanced `create_line_chart()` with threshold support
- `src/utils/technical_indicators.py`: Removed `calculate_macd`

---

### Modular Agent Tools Architecture (v5.0)

**Revolutionary Refactor - Complete Layer Separation:**

**Before (Coupled):**
```python
# TrendAgent had monolithic methods
class TrendAgent:
    def get_yf_data(...)          # Fetch + analyze + chart
    def get_fred_data(...)         # Fetch + analyze + chart
    def _get_technical_indicators(...)  # Tightly coupled
```

**After (Modular):**
```python
# 7 independent @function_tool in agent_tools.py (v6.0: removed MACD)
@function_tool async def fetch_data(source, symbol, period)
@function_tool async def analyze_OHLCV_data(source, symbol, period)
@function_tool async def generate_OHLCV_chart(source, symbol, period)
@function_tool async def analyze_SMA_data(symbol, period, windows)
@function_tool async def analyze_disparity_data(symbol, period, window)  # v6.0: dynamic thresholds
@function_tool async def analyze_RSI_data(symbol, period, window)        # v6.0: dynamic thresholds
@function_tool async def generate_disparity_chart(symbol, period, window)  # v6.0: threshold visualization
@function_tool async def generate_RSI_chart(symbol, period, window)        # v6.0: threshold visualization
```

**Design Principles:**
1. **Layer Separation**: Data fetching ↔ Analysis ↔ Chart generation completely decoupled
2. **Agent Autonomy**: Each agent selects only the tools it needs
3. **Cache-Based**: Fetch once (longest period first), then all tools reuse cached data
4. **Modularity**: Adding new indicators = adding new independent tools
5. **Zero Coupling**: `technical_indicators.py` only has pure functions

**Agent-Specific Tool Selection:**
```python
# TNXAgent: Basic OHLCV + SMA
tools=[fetch_data, analyze_OHLCV_data, generate_OHLCV_chart, analyze_SMA_data]

# EquityTrendAgent: Full suite including disparity and RSI
tools=[
    fetch_data, analyze_OHLCV_data, generate_OHLCV_chart,
    analyze_SMA_data, analyze_disparity_data, generate_disparity_chart,
    generate_RSI_chart, analyze_RSI_data
]

# NFCIAgent: FRED-only (no technical indicators)
tools=[fetch_data, analyze_OHLCV_data, generate_OHLCV_chart]
```

**Benefits:**
- ✅ **Flexibility**: Mix and match tools per agent
- ✅ **Maintainability**: Single Responsibility per tool
- ✅ **Extensibility**: Add tools without touching existing code
- ✅ **Testability**: Each tool independently testable
- ✅ **Performance**: Cached data reused across all tool calls

**Deprecated & Removed:**
- `TrendAgent.get_yf_data()`, `TrendAgent.get_fred_data()` ❌
- `TrendAgent._get_technical_indicators()` ❌
- `TrendAgent._create_yfinance_indicators_tool()` ❌
- `TechnicalAnalyzer` class (fluent API) ❌
  - Replaced with pure functions: `calculate_sma()`, `calculate_disparity()`, etc.

**Files:**
- **New**: `src/agent/tools/agent_tools.py` (v6.0: 7 tools with dynamic thresholds)
- **Modified**: `src/agent/base/trend_agent.py` (simplified to 112 lines, added label/description)
- **Modified**: All trend agents (TNX, DX, NFCI, Equity) with tool selection and labels
- **Modified**: `src/utils/technical_indicators.py` (removed MACD, pure functions remain)

---

### SMA(200) Chart Fix (v4.1)

**Problem Solved:**
- **SMA_200 lines were cut off** at the beginning of 1y charts for TNX and DX=F
- Issue: Insufficient historical data buffer causing rolling average calculation to start from chart start date

**Solution:**
1. **Extended Data Fetching**: Fetch 220+ *business days* (not calendar days) before display period
   - Used `pandas.tseries.offsets.BDay` for accurate trading day calculation
   - Additional 20 business day margin to handle holidays/market closures
2. **Pre-compute SMAs**: Calculate SMA (5, 20, 200) on full buffered history *before* slicing for display
3. **Smart Slicing Logic**: Display starts from the later of:
   - Requested start date (e.g., 1 year ago)
   - First valid SMA_200 date (199 business days into fetched data)
4. **Fixed Test Data**: Corrected mock DataFrame generation to avoid NaN Close values

**Results:**
- ✅ TNX 1y chart: SMA_200 displayed from first row (no cut-off)
- ✅ DX=F 1y chart: SMA_200 displayed from first row (no cut-off)
- ✅ All unit tests passing with 0 null SMA values in display window
- ✅ Charts show complete SMA lines across entire display period

**Files Modified:**
- `src/utils/data_sources.py`: Enhanced fetch logic with BDay offset, removed redundant slicing condition
- `src/utils/data_sources_test.py`: Fixed mock data generation (list comprehension instead of Series misalignment)

### Chart Separation & Disparity Features (v4.0)

**Chart System Refactor:**
- **Separated Chart Functions**: Dedicated functions per data type
  - `create_yfinance_chart()`: Candlestick with SMA overlays
  - `create_fred_chart()`: Line chart with baseline
  - `create_line_chart()`: Generic line chart for technical indicators (disparity, RSI, MACD)
- **DataSource Purity**: `fetch_data()` returns raw OHLCV only, no calculations

**Equity-Specific Features:**
- **200-day Disparity (이격도)** available as independent tool
- **Separate Disparity Chart**: Visual representation of price vs SMA relationship
- Formula: `(Current Price / SMA_200 - 1) * 100`
- Interpretation: >0% = above long-term average, <0% = below
- Accessible via `analyze_disparity_data()` and `generate_disparity_chart()` tools

**Pythonic Improvements:**
- Python 3.13 compatible (using builtin `list`, `dict` types)
- Type hints with modern syntax (`list[int]`, `dict[str, float]`)
- Single Responsibility Principle per function

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
from src.agent.orchestrator import LiquidityAgent, BroadIndexAgent, MarketReportAgent

# Initialize agents
tnx_agent = TNXAgent()                      # ^TNX analysis with label "10-Year Treasury Yield"
nfci_agent = NFCIAgent()                    # NFCI analysis with label "National Financial Conditions Index"
dx_agent = DXAgent()                        # DX=F analysis with label "US Dollar Index"
equity_agent = EquityTrendAgent(
    "NVDA", 
    label="NVIDIA"
)                                           # NVDA analysis with custom label
equity_etf = EquityTrendAgent(
    "IAU",
    label="iShares Gold Trust",
    description="Gold-tracking ETF"
)                                           # IAU with label and description
liquidity_agent = LiquidityAgent()          # TNX + NFCI + DX orchestrator
broad_index_agent = BroadIndexAgent()       # S&P 500 + Nasdaq + Dow Jones orchestrator
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
- ✅ **ReportBuilder**: 2 tests (parent page creation, failure handling)
- ✅ **ImageService**: 4 tests (Cloudflare R2 upload, local image finding)
- ✅ **DataSources**: 12 tests (yfinance/FRED with Mock API, SMA calculations, SMA(200) cut-off tests)
- ✅ **Charts**: 7 tests (candlestick charts, SMA overlays, weekend gap removal)
- ✅ **Total**: 51 comprehensive tests (0.6s execution time)
- ⚠️ **Notion Upload Test**: Only runs when `TEST_MODE=true` (prevents creating pages during normal testing)
- 🚫 **No Real API Calls**: All tests use Mock data for fast, reliable execution

**Test Explorer**: Use VS Code/Cursor Test Explorer (configured in `.vscode/settings.json`)

**Recent Test Results:**
```
# Data Sources Tests
Ran 12 tests in 0.015s
OK

# Charts Tests  
Ran 7 tests in 0.590s
OK

# All Tests Combined
Ran 51 tests in 0.606s
OK
✅ All tests passed (includes SMA(200) cut-off tests)
```

