# Changelog

All notable changes to this project will be documented in this file.

---

## v7.3 - Market Health Monitor & Score System

**Date: November 10, 2025**

### Major Updates

**1. Market Health Monitor Agent:**
- **New Agent**: `MarketHealthAgent` in `src/agent/orchestrator/market_health_agent.py`
  - Synthesizes 5 contrarian indicators: Bull-Bear Spread, Put/Call Ratio, Margin Debt, High Yield Spread, VIX
  - Composite score calculation (0 to 5 range)
  - Market status: STRONG_BUY / BUY / NEUTRAL / CAUTION / STRONG_SELL
  - Structured output with charts/tables from each sub-agent

**2. BroadIndexAgent Refactoring:**
- **Agent Simplified**: Contrarian indicators moved from `BroadIndexAgent` to `MarketHealthAgent`
  - Before: 3 major indices + 6 market indicators (9 agents)
  - After: 3 major indices + MarketBreadthAgent (4 agents)
  - Better separation of concerns: indices vs contrarian sentiment

**3. Score System Infrastructure:**
- **Enhanced Type**: `AnalysisReport` now includes optional `score: float | None` field
  - TrendAgent: Individual indicator score
  - OrchestratorAgent: Composite aggregated score
  - Strict JSON schema compatible

### Impact
- ✅ Single view for overall market health across 5 contrarian indicators
- ✅ Better separation: BroadIndexAgent (indices) vs MarketHealthAgent (sentiment/risk)
- ✅ Quantified composite scoring for systematic decision-making
- ✅ Flexible score infrastructure (float type) for future agent expansions

---

## v7.2 - High Yield Spread & VIX Agents + Sentiment Refactoring

**Date: November 9, 2025**

### Major Updates

**1. High Yield Spread Agent:**
- **New Agent**: `HighYieldSpreadAgent` in `src/agent/trend/high_yield_spread_agent.py`
  - FRED data source: `BAMLH0A0HYM2` (ICE BofA US High Yield Index)
  - Credit risk and contrarian sentiment indicator
  - Critical thresholds: >5% (alert), >7% (crisis), Peak→Declining (buy)
  - 10-year historical analysis for long-term perspective
- **New Tools**: `analyze_high_yield_spread`, `generate_high_yield_spread_chart`
  - Analysis periods: 6mo, 1y tables | 10y chart
  - Leads equity market by 1-2 months during stress periods

**2. VIX Agent:**
- **New Agent**: `VIXAgent` in `src/agent/trend/vix_agent.py`
  - YFinance data source: `^VIX` (CBOE Volatility Index)
  - Market fear gauge and contrarian indicator
  - Critical thresholds: >30 (extreme fear/buy), <12 (complacency/sell)
  - 2,512 data points covering 10 years of volatility history
- **New Tools**: `analyze_vix`, `generate_vix_chart`
  - Analysis periods: 5d, 1mo tables | 1y chart
  - Inversely correlates with S&P 500, spikes mark market bottoms

**3. Sentiment Agent Refactoring:**
- **Renamed**: `SentimentAgent` → `BullBearSpreadAgent`
  - More descriptive naming (Bull-Bear Spread vs generic Sentiment)
  - Function renaming: `analyze_sentiment` → `analyze_bull_bear_spread`
  - Function renaming: `generate_sentiment_chart` → `generate_bull_bear_spread_chart`

**4. Bug Fixes:**
- Fixed pandas FutureWarning in volatility calculations
- Added `fill_method=None` to `pct_change()` calls

### Impact
- ✅ 3 new sentiment/volatility indicators for comprehensive market analysis
- ✅ Credit risk monitoring with 5%/7% alert thresholds
- ✅ VIX fear gauge for contrarian market timing (>30 buy signal)
- ✅ Clearer agent naming (Bull-Bear Spread vs generic Sentiment)
- ✅ No deprecation warnings

---

## v7.1 - FINRA Margin Debt Integration

**Date: November 8, 2025**

### Major Updates

**1. FINRA Margin Statistics Data Source:**
- **New DataSource**: `FINRASource` in `src/data_sources/web/finra_source.py`
  - Web scraping from finra.org margin statistics page
  - Symbol: `MARGIN_DEBT_YOY` (Year-over-Year change percentage)
  - Automatic YoY calculation (12-month pct_change)
  - File-based caching with `_validated` flag
  - Extensible SYMBOL_CONFIG structure for future additions
- **Historical Data**: `data/margin_debt_history.json`
  - 333 monthly data points (1998-01 ~ 2025-09)
  - Latest: +38.52% YoY (approaching extreme leverage zone)
  - Format unified with other web sources

**2. Margin Debt Analysis Agent:**
- **New Agent**: `MarginDebtAgent` in `src/agent/trend/margin_debt_agent.py`
  - Contrarian sentiment indicator (leverage as market overheating signal)
  - Critical thresholds:
    * 🔴 Sell: YoY > +50% | Peak → below 50%
    * 🟡 Buy: YoY < -20% | YoY < -30% | Trough → above -20%
  - Historical leading indicator (1-3 months before market moves)
- **New Tools**: `analyze_margin_debt`, `generate_margin_debt_chart`
  - Analysis periods: 6mo tables, 10y charts
  - Threshold visualization: +50% (Extreme Leverage), -20% (Deleveraging)

**3. Chart Filename Bug Fix:**
- **Problem**: `%` symbol in filenames broke URL loading in Notion
  - `Margin_Debt_YoY_%_10y_chart.png` → Failed to load
- **Solution**: Replace `%` with `pct` in all chart generation functions
  - `Margin_Debt_YoY_pct_10y_chart.png` → Loads successfully
- **Applied to**: `create_yfinance_chart`, `create_fred_chart`, `create_line_chart`

**4. Testing:**
- 6 comprehensive tests for FINRA data source
- Mock scraping, cache validation, error handling
- All tests passing

### Impact
- ✅ Margin Debt as contrarian leverage indicator (빚투 지표)
- ✅ 333 months of historical data (1998-2025) for long-term analysis
- ✅ Chart filename URL compatibility fixed (% → pct)
- ✅ Extensible structure for future FINRA indicators

---

## v7.0 - Put/Call Ratio & Unified Chart/Cache Systems

**Date: November 8, 2025**

### Major Updates

**1. CBOE Equity Put/Call Ratio Integration:**
- **New DataSource**: `YChartsSource` in `src/data_sources/web/ycharts_source.py`
  - Web scraping from ycharts.com
  - CBOE Equity Put/Call Ratio (contrarian sentiment indicator)
  - 2-3 months of historical data (50 records)
  - Weekend-aware caching with business day logic
- **New Agent**: `PutCallAgent` in `src/agent/trend/put_call_agent.py`
  - Integrated into BroadIndexAgent
  - Thresholds: >1.5 (Bearish Sentiment), <0.5 (Bullish Sentiment)
- **New Tools**: `analyze_put_call`, `generate_put_call_chart`
- **Data File**: `data/put_call_ratio_history.json` (50 records)

**2. Unified Chart Generation System:**
- **chart_type Parameter**: All DataSources now support `chart_type`
  - `'candle'`: YFinance OHLCV candlestick charts (default for stocks)
  - `'line'`: Line charts for all other data (default for FRED, web sources)
- **Flexible Options via kwargs**: `threshold_upper`, `threshold_lower`, `overbought_label`, `oversold_label`, `value_format`, `ylabel`
- **Generic create_chart()**: Truly universal across all data sources
  - YFinanceSource: Supports both 'candle' and 'line' types
  - FREDSource: 'line' with baseline support
  - WebDataSources: 'line' with threshold support
- **agent_tools.py**: Sets all chart parameters explicitly
  - Disparity & RSI now use `YFinanceSource.create_chart(type='line')`
  - No more direct `create_line_chart()` calls from agent_tools

**3. Function Naming Unification:**
- **analyze Functions**: Removed 'data' suffix for consistency
  - `analyze_OHLCV_data` → `analyze_OHLCV`
  - `analyze_SMA_data` → `analyze_SMA`
  - `analyze_disparity_data` → `analyze_disparity`
  - `analyze_RSI_data` → `analyze_RSI`
  - `analyze_put_call_ratio` → `analyze_put_call`
- **generate Functions**: Kept 'chart' suffix for clarity
  - All remain as `generate_XXX_chart`
- **NFCI Dedicated Functions**: `analyze_NFCI`, `generate_NFCI_chart`
  - Separated from generic OHLCV functions
  - `generate_OHLCV_chart` now YFinance-specific

**4. Web Source JSON Format Unification:**
- **market_breadth_history.json**: Changed from object to array format
- **Unified Format**: All web sources now use `[{"date": "YYYY-MM-DD", "value": float}]`
- **Top-level _validated**: Moved validation flag to root level

**5. Web Source Cache Consolidation:**
- Generic cache methods moved to `WebDataSource` base class
- Removed 131 lines of duplicate code

### Impact
- ✅ Put/Call Ratio as contrarian sentiment indicator
- ✅ Generic chart generation across all data sources
- ✅ Consistent function naming (analyze_XXX, generate_XXX_chart)
- ✅ Unified JSON format for all web sources
- ✅ Code deduplication and improved maintainability

---

## v6.4 - Chart Period Accuracy & Data Consistency

**Date: November 6, 2025**

### Major Updates

**1. Actual Period Calculation System:**
- **New Method**: `DataSource.get_actual_period_approx(data)`
  - Automatically calculates actual data range from fetched data
  - Approximates to nearest standard period (5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y)
  - Works consistently across all data sources

**2. Dynamic Period Detection:**
- **Problem**: Requested "5y" but actual data only 2 months → Chart showed "5 Years" (misleading)
- **Solution**: All charts now display actual data period
  - Example: Request "5y" → Get 56 days → Display "1 Month"

**3. Chart Improvements:**
- **Invalid Data Filtering**: Filters out incomplete data rows
- **Continuous X-axis**: Integer positions (no weekend gaps)
- **NaN Handling**: Automatic removal
- **Consistent Date Format**: `%Y-%m-%d` format

### Impact
- ✅ Chart titles accurately reflect actual data period
- ✅ Cleaner chart rendering
- ✅ Consistent data access across all sources

---

## v6.3 - P/E & PEG (NTM) Chart Capture with Headless Fix

**Date: November 5, 2025**

### Major Updates

**1. Enhanced P/E & PEG (NTM) Chart Generation:**
- **Tool**: `generate_PE_PEG_ratio_chart(ticker, period='10Y')`
  - Captures both P/E (NTM) and PEG (NTM) with Historical Price overlay
  - Flexible period selection: 1Y, 3Y, 5Y, 10Y, 20Y

**2. Headless Mode Fix:**
- **Problem**: Headless `maximize_window()` doesn't work
- **Solution**: Detect screen size, fallback to 1920x1080
- **Result**: Headless mode now works reliably

---

## v6.2 - Forward P/E (NTM) Analysis & FinnhubSource

**Date: November 3, 2025**

### Major Updates

**1. Forward P/E (NTM) Chart via Koyfin Automation:**
- Selenium + Firefox automation (~12-15 seconds per ticker)
- 10-year Forward P/E ratio + Historical Price overlay

**2. FinnhubSource Data Layer:**
- Forward P/E calculation from EPS estimates

### Limitations
- ⚠️ Selenium dependency (brittle to UI changes)
- ⚠️ No free API for historical Forward P/E data

---

## v6.1 - Markdown Link Parsing & Agent Instruction Refactoring

**Date: November 3, 2025**

### Major Updates

**1. Markdown Hyperlink Support:**
- Auto-convert `[text](https://...)` → Notion hyperlinks
- Auto-convert standalone URLs → clickable links
- Chart links preserved for R2 embeds

**2. TrendAgent Instruction Refactoring:**
- Moved common instructions to base class
- Subclass instructions simplified

**3. Orchestrator Content Preservation:**
- Explicit rules for preserving chart/reference links

---

## v6.0 - Dynamic Thresholds & Agent Enhancements

**Date: October 31, 2025**

### Major Updates

**1. BroadIndexAgent:**
- New orchestrator for S&P 500, Nasdaq, Dow Jones

**2. TrendAgent Label & Description:**
- Added `label` for human-readable names
- Added `description` for brief context

**3. Dynamic Thresholds:**
- RSI: 80th/10th percentile (vs fixed 70/30)
- Disparity: 80th/10th percentile (vs fixed ±20%)

**4. Code Cleanup:**
- Removed MACD functions

---

## v5.0 - Modular Agent Tools Architecture

**Revolutionary Refactor - Complete Layer Separation**

### Before (Coupled)
```python
class TrendAgent:
    def get_yf_data(...)   # Fetch + analyze + chart
```

### After (Modular)
```python
# 7 independent @function_tool
@function_tool async def fetch_data(source, symbol, period)
@function_tool async def analyze_OHLCV(source, symbol, period)
@function_tool async def generate_OHLCV_chart(source, symbol, period)
```

### Design Principles
1. Layer Separation: Data ↔ Analysis ↔ Chart completely decoupled
2. Agent Autonomy: Each agent selects needed tools
3. Cache-Based: Fetch once, reuse cached data
4. Zero Coupling: Pure functions only

---

## v4.1 - SMA(200) Chart Fix

**Problem**: SMA_200 lines cut off at chart beginning
**Solution**: Extended data fetching (220+ business days buffer)

---

## v4.0 - Chart Separation & Disparity Features

### Chart System Refactor
- Separated chart functions per data type
- Added 200-day Disparity tool
- Python 3.13 compatible

---

## v3.0 - SMA (Simple Moving Averages) Implementation

### Technical Analysis Enhancement
- 5-day, 20-day, 200-day SMAs
- Candlestick charts with SMA overlays
- Conditional SMA display based on period
- Weekend gap removal

---

## v2.0 - Advanced Markdown Parsing

### 3-Level Nested List Support
- Smart hierarchy detection
- Pythonic recursive parsing
- Notion API compatibility
- 30 comprehensive tests

---

## Earlier Versions

For version history before v2.0, see git commit history.

