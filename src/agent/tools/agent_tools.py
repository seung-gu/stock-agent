from agents import function_tool

from src.utils.data_sources import get_data_source
from src.utils.technical_indicators import calculate_rsi, calculate_disparity
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
async def generate_OHLCV_chart(source: str, symbol: str, period: str, label: str = None) -> str:
    """
    Create chart from cached data only and return 'Chart saved: ...' path.
    
    Args:
        source: Data source ("yfinance" or "fred")
        symbol: Symbol or indicator code
        period: Time period
        label: Human-readable label for chart title (optional, defaults to symbol)
    """
    src = get_data_source(source)
    data = await src.fetch_data(symbol, period)
    chart_info = await src.create_chart(data, symbol, period, label=label)
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
    """
    Build disparity indicator text with dynamic overbought/oversold levels.
    Returns current disparity with 80th percentile (overbought) and 10th percentile (oversold) thresholds.
    """
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    disp = calculate_disparity(hist, window=window)
    
    if disp.empty or disp.iloc[-1] != disp.iloc[-1]:
        return ""
    
    current_disp = float(disp.iloc[-1])
    
    # Calculate historical percentiles for dynamic thresholds
    upper_threshold = float(disp.quantile(0.80))  # 80th percentile (overbought)
    lower_threshold = float(disp.quantile(0.10))  # 10th percentile (oversold)
    
    return (f"Disparity({window}): {current_disp:.2f}% "
            f"[Overbought>{upper_threshold:.1f}%, Oversold<{lower_threshold:.1f}%]")


@function_tool
async def analyze_RSI_data(symbol: str, period: str, window: int = 14) -> str:
    """
    Build RSI indicator text with dynamic overbought/oversold levels.
    Returns current RSI with 80th percentile (overbought) and 20th percentile (oversold) thresholds.
    """
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    rsi = calculate_rsi(hist, window=window)
    
    if rsi.empty or rsi.iloc[-1] != rsi.iloc[-1]:
        return ""
    
    current_rsi = float(rsi.iloc[-1])
    
    # Calculate historical percentiles for dynamic thresholds
    upper_threshold = float(rsi.quantile(0.80))  # 80th percentile (overbought)
    lower_threshold = float(rsi.quantile(0.10))  # 10th percentile (oversold)
    
    return (f"RSI({window}): {current_rsi:.2f} "
            f"[Overbought>{upper_threshold:.1f}, Oversold<{lower_threshold:.1f}]")


@function_tool
async def generate_disparity_chart(symbol: str, period: str = "5y", window: int = 200, label: str = None) -> str:
    """Generate disparity line chart with dynamic overbought/oversold threshold lines."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    series = calculate_disparity(hist, window=window)
    if series.empty:
        return f"{symbol} disparity data not available"
    
    # Calculate dynamic thresholds
    upper_threshold = float(series.quantile(0.80))
    lower_threshold = float(series.quantile(0.10))
    
    return create_line_chart(
        data=series.to_frame(name=f"Disparity_{window}"),
        label=f"{label or symbol} Disparity_{window}",
        ylabel="Disparity from SMA (%)",
        period=period,
        overbought_label="Overbought",
        oversold_label="Oversold",
        data_column=f"Disparity_{window}",
        threshold_upper=upper_threshold,
        threshold_lower=lower_threshold
    )


@function_tool
async def generate_RSI_chart(symbol: str, period: str, window: int = 14, label: str = None) -> str:
    """Generate RSI line chart with dynamic overbought/oversold threshold lines."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['history']
    series = calculate_rsi(hist, window=window)
    if series.empty:
        return f"{symbol} RSI data not available"
    
    # Calculate dynamic thresholds
    upper_threshold = float(series.quantile(0.80))
    lower_threshold = float(series.quantile(0.10))
    
    return create_line_chart(
        data=series.to_frame(name=f"RSI_{window}"),
        label=f"{label or symbol} RSI_{window}",
        ylabel="RSI",
        period=period,
        overbought_label="Overbought",
        oversold_label="Oversold",
        data_column=f"RSI_{window}",
        threshold_upper=upper_threshold,
        threshold_lower=lower_threshold
    )

