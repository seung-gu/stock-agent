from agents import function_tool

from src.utils.data_sources import get_data_source
from src.utils.technical_indicators import calculate_sma, calculate_rsi, calculate_disparity, calculate_macd
from src.utils.charts import create_line_chart


def get_period_name(period: str) -> str:
    period_names = {
        "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
        "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
    }
    return period_names.get(period, f"{period}")


@function_tool
async def fetch_data(source: str, symbol: str, period: str) -> str:
    """Populate cache by fetching the longest period first (unified for yf/FRED)."""
    src = get_data_source(source)
    await src.fetch_data(symbol, period)
    return f"Fetched OK for {source}:{symbol} {period}"


@function_tool
async def analyze_OHLCV_data(source: str, symbol: str, period: str) -> str:
    """Analyze cached data and return OHLCV(Open, High, Low, Close, Volatility) analysis."""
    src = get_data_source(source)
    data = await src.fetch_data(symbol, period)
    analysis = src.get_analysis(data, period)
    period_name = get_period_name(period)
    # Indicators are source-specific; keep outside (e.g., TrendAgent.indicators_yf)
    return f"""{period_name} Analysis ({symbol}):
            - Start: {analysis['start']:.3f}
            - End: {analysis['end']:.3f}
            - Change: {analysis['change_pct']:+.2f}%
            - High: {analysis['high']:.3f}
            - Low: {analysis['low']:.3f}
            - Volatility: {analysis['volatility']:.3f}"""


@function_tool
async def generate_OHLCV_chart(source: str, symbol: str, period: str) -> str:
    """Create chart from cached data only and return 'Chart saved: ...' path."""
    src = get_data_source(source)
    data = await src.fetch_data(symbol, period)
    chart_info = await src.create_chart(data, symbol, period)
    return chart_info


@function_tool
async def analyze_SMA_data(symbol: str, period: str, windows: list[int] = [5, 20, 200]) -> str:
    """Build SMA indicators text using cached yfinance data."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    parts = []
    for w in windows:
        col = f"SMA_{w}"
        if col in hist.columns and not hist[col].empty and hist[col].iloc[-1] == hist[col].iloc[-1]:
            parts.append(f"SMA({w}): {float(hist[col].iloc[-1]):.3f}")
    return ", ".join(parts)


@function_tool
async def analyze_disparity_data(symbol: str, period: str, window: int = 200) -> str:
    """Build disparity indicator text using cached yfinance data."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    disp = calculate_disparity(hist, window=window)
    if not disp.empty and disp.iloc[-1] == disp.iloc[-1]:
        return f"Disparity({window}): {float(disp.iloc[-1]):.2f}%"
    return ""


@function_tool
async def analyze_RSI_data(symbol: str, period: str, window: int = 14) -> str:
    """Build RSI indicator text using cached yfinance data."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    rsi = calculate_rsi(hist, window=window)
    if not rsi.empty and rsi.iloc[-1] == rsi.iloc[-1]:
        return f"RSI({window}): {float(rsi.iloc[-1]):.2f}"
    return ""


@function_tool
async def generate_disparity_chart(symbol: str, period: str = "5y", window: int = 200) -> str:
    """Generate disparity line chart from cached yfinance data and return saved path."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    series = calculate_disparity(hist, window=window)
    if series.empty:
        return f"{symbol} disparity data not available"
    # create chart using generic line chart
    title = f"{symbol}_Disparity_{window}"
    return create_line_chart(
        data=series.to_frame(name=f"Disparity_{window}"),
        title=title,
        ylabel="Disparity from SMA (%)",
        period=period,
        value_format="{:.2f}%",
        baseline=0,
        positive_label="Above SMA",
        negative_label="Below SMA",
        data_column=f"Disparity_{window}"
    )


@function_tool
async def analyze_MACD_data(symbol: str, period: str, fast: int = 12, slow: int = 26, signal: int = 9) -> str:
    """Build MACD indicators text using cached yfinance data."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    macd = calculate_macd(hist, fast=fast, slow=slow, signal=signal)
    macd_val = macd['macd'].iloc[-1]
    signal_val = macd['signal'].iloc[-1]
    hist_val = macd['histogram'].iloc[-1]
    if macd_val == macd_val and signal_val == signal_val and hist_val == hist_val:
        return f"MACD({fast},{slow},{signal}): {float(macd_val):.3f}, Signal: {float(signal_val):.3f}, Hist: {float(hist_val):.3f}"
    return ""


@function_tool
async def generate_RSI_chart(symbol: str, period: str, window: int = 14) -> str:
    """Generate RSI line chart from cached yfinance data and return saved path."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    series = calculate_rsi(hist, window=window)
    if series.empty:
        return f"{symbol} RSI data not available"
    title = f"{symbol}_RSI_{window}"
    return create_line_chart(
        data=series.to_frame(name=f"RSI_{window}"),
        title=title,
        ylabel="RSI",
        period=period,
        value_format="{:.2f}",
        baseline=50,
        positive_label="Above 50",
        negative_label="Below 50",
        data_column=f"RSI_{window}"
    )


@function_tool
async def generate_MACD_chart(symbol: str, period: str, fast: int = 12, slow: int = 26, signal: int = 9) -> str:
    """Generate MACD line chart from cached yfinance data and return saved path."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    macd = calculate_macd(hist, fast=fast, slow=slow, signal=signal)
    # Plot MACD line (use generic line chart for the MACD series only for simplicity)
    series = macd['macd']
    if series.empty:
        return f"{symbol} MACD data not available"
    title = f"{symbol}_MACD_{fast}_{slow}_{signal}"
    return create_line_chart(
        data=series.to_frame(name=f"MACD_{fast}_{slow}_{signal}"),
        title=title,
        ylabel="MACD",
        period=period,
        value_format="{:.3f}",
        baseline=0,
        positive_label="Above 0",
        negative_label="Below 0",
        data_column=f"MACD_{fast}_{slow}_{signal}"
    )

