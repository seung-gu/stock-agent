import asyncio
import os
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from agents import function_tool
from factset_report_analyzer import SP500
from factset_report_analyzer.utils.plot import plot_time_series

from src.data_sources import get_data_source
from src.config import CHART_OUTPUT_DIR
from src.utils.technical_indicators import calculate_rsi, calculate_disparity
from src.utils.koyfin_chart_capture import KoyfinChartCapture


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
async def analyze_OHLCV(source: str, symbol: str, period: str) -> str:
    """Analyze cached data and return OHLCV(Open, High, Low, Close, Volatility) analysis."""
    src = get_data_source(source)
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
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
        source: Data source ("yfinance" only - for FRED, use generate_NFCI_chart)
        symbol: Symbol or indicator code
        period: Time period
        label: Human-readable label for chart title (optional, defaults to symbol)
    """
    src = get_data_source(source)
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    
    # Get chart config for yfinance
    info = data.get('info', {})
    chart_config = src._get_chart_config(symbol, info)
    
    chart_info = await src.create_chart(
        data, symbol, actual_period, 
        label=label,
        ylabel=chart_config['ylabel'],
        value_format=chart_config['value_format']
    )
    return chart_info


@function_tool
async def analyze_SMA(symbol: str, period: str, windows: list[int] = [5, 50, 200]) -> str:
    """Build SMA indicators text using cached yfinance data."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['data']
    parts = []
    for w in windows:
        col = f"SMA_{w}"
        if col in hist.columns and not hist[col].empty and hist[col].iloc[-1] == hist[col].iloc[-1]:
            parts.append(f"SMA({w}): {float(hist[col].iloc[-1]):.3f}")
            
    return ", ".join(parts)


@function_tool
async def analyze_disparity(symbol: str, period: str, window: int = 200) -> str:
    """
    Build disparity indicator text with dynamic overbought/oversold levels.
    Returns current disparity with 80th percentile (overbought) and 10th percentile (oversold) thresholds.
    """
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['data']
    disp = calculate_disparity(hist, window=window)
    
    if disp.empty or disp.iloc[-1] != disp.iloc[-1]:
        return ""
    
    current_disp = float(disp.iloc[-1])
    current_disp_rank = float(disp.rank(pct=True).iloc[-1] * 100)
    
    # Calculate historical percentiles for dynamic thresholds
    upper_threshold = float(disp.quantile(0.80))  # 80th percentile (overbought)
    lower_threshold = float(disp.quantile(0.10))  # 10th percentile (oversold)
    
    return (f"Disparity({window}): {current_disp:.2f}% (Rank: {current_disp_rank:.1f}%) "
            f"[Overbought>{upper_threshold:.1f}%, Oversold<{lower_threshold:.1f}%]")
    

@function_tool
async def generate_disparity_chart(symbol: str, period: str = "5y", window: int = 200, label: str = None) -> str:
    """Generate disparity line chart with dynamic overbought/oversold threshold lines."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['data']
    series = calculate_disparity(hist, window=window)
    if series.empty:
        return f"{symbol} disparity data not available"
    
    # Calculate actual period from the final series (after disparity calculation removes NaN)
    actual_period = src.get_actual_period_approx({'data': series})
    
    # Calculate dynamic thresholds
    upper_threshold = float(series.quantile(0.80))
    lower_threshold = float(series.quantile(0.10))
    
    # Create modified data dict with calculated disparity series
    disparity_data = {
        'data': series.to_frame(name=f"Disparity{window}"),
        'info': data['info']
    }
    
    chart_path = await src.create_chart(
        disparity_data, symbol, actual_period,
        label=f"{label or symbol} Disparity{window}",
        chart_type='line',
        ylabel='Disparity from SMA (%)',
        data_column=f"Disparity{window}",
        threshold_upper=upper_threshold,
        threshold_lower=lower_threshold,
        overbought_label="Overbought",
        oversold_label="Oversold"
    )
    
    return chart_path


@function_tool
async def analyze_RSI(symbol: str, period: str, window: int = 14) -> str:
    """
    Build RSI indicator text with dynamic overbought/oversold levels.
    Returns current RSI with 80th percentile (overbought) and 20th percentile (oversold) thresholds.
    """
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['data']
    rsi = calculate_rsi(hist, window=window)
    
    if rsi.empty or rsi.iloc[-1] != rsi.iloc[-1]:
        return ""
    
    current_rsi = float(rsi.iloc[-1])
    current_rsi_rank = float(rsi.rank(pct=True).iloc[-1] * 100)
    
    # Calculate historical percentiles for dynamic thresholds
    upper_threshold = float(rsi.quantile(0.80))  # 80th percentile (overbought)
    lower_threshold = float(rsi.quantile(0.10))  # 10th percentile (oversold)
    
    return (f"RSI({window}): {current_rsi:.2f} (Rank: {current_rsi_rank:.1f}%) "
            f"[Overbought>{upper_threshold:.1f}, Oversold<{lower_threshold:.1f}]")


@function_tool
async def generate_RSI_chart(symbol: str, period: str, window: int = 14, label: str = None) -> str:
    """Generate RSI line chart with dynamic overbought/oversold threshold lines."""
    src = get_data_source("yfinance")
    data = await src.fetch_data(symbol, period)
    hist = data['data']
    series = calculate_rsi(hist, window=window)
    if series.empty:
        return f"{symbol} RSI data not available"
    
    # Calculate actual period from the final series (after RSI calculation removes NaN)
    actual_period = src.get_actual_period_approx({'data': series})
    
    # Calculate dynamic thresholds
    upper_threshold = float(series.quantile(0.80))
    lower_threshold = float(series.quantile(0.10))
    
    # Create modified data dict with calculated RSI series
    rsi_data = {
        'data': series.to_frame(name=f"RSI{window}"),
        'info': data['info']
    }
    
    chart_path = await src.create_chart(
        rsi_data, symbol, actual_period,
        label=f"{label or symbol} RSI{window}",
        chart_type='line',
        ylabel='RSI',
        data_column=f"RSI{window}",
        threshold_upper=upper_threshold,
        threshold_lower=lower_threshold,
        overbought_label="Overbought",
        oversold_label="Oversold"
    )
    
    return chart_path


@function_tool
async def analyze_NFCI(period: str) -> str:
    """Analyze NFCI (National Financial Conditions Index).
    
    Args:
        period: Time period (6mo, 1y, 2y, etc.)
    """
    src = get_data_source('fred')
    data = await src.fetch_data('NFCI', period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    return f"""{period_name} NFCI (National Financial Conditions Index):
            - Start: {analysis['start']:.3f}
            - End: {analysis['end']:.3f}
            - Change: {analysis['change_pct']:+.2f}%
            - High: {analysis['high']:.3f}
            - Low: {analysis['low']:.3f}"""


@function_tool
async def generate_NFCI_chart(period: str) -> str:
    """Generate NFCI (National Financial Conditions Index) chart.
    
    Args:
        period: Time period (6mo, 1y, 2y, etc.)
    """
    src = get_data_source('fred')
    data = await src.fetch_data('NFCI', period)
    actual_period = src.get_actual_period_approx(data)
    
    chart_info = await src.create_chart(
        data, 'NFCI', actual_period,
        label='National Financial Conditions Index',
        baseline=0.0,
        positive_label='Tighter Conditions',
        negative_label='Looser Conditions'
    )
    return chart_info


@function_tool
async def analyze_market_breadth(symbol: str, period: str) -> str:
    """Analyze S&P 500 market breadth data (% stocks above MA).
    
    Args:
        symbol: 'S5FI' (50-day MA) or 'S5TH' (200-day MA)
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('investing')
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    ma_period = analysis['ma_period']
    
    return f"""{period_name} Market Breadth ({symbol} - {ma_period}day MA):
            - Start: {analysis['start']:.2f}%
            - End: {analysis['end']:.2f}%
            - Change: {analysis['change']:+.2f}%
            - High: {analysis['high']:.2f}%
            - Low: {analysis['low']:.2f}%"""


@function_tool
async def generate_market_breadth_chart(symbol: str, period: str) -> str:
    """Generate S&P 500 market breadth chart (% stocks above MA).
    
    Args:
        symbol: 'S5FI' (50-day MA) or 'S5TH' (200-day MA)
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('investing')
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    
    # Determine label based on symbol
    ma_period = data['ma_period']
    label = f"S&P 500 Stocks Above {ma_period}-Day MA"
    
    chart_info = await src.create_chart(
        data, symbol, actual_period,
        label=label,
        ylabel='Percentage (%)',
        data_column='Breadth',
        threshold_upper=70.0,
        threshold_lower=30.0,
        overbought_label='Strong Breadth',
        oversold_label='Weak Breadth'
    )
    return chart_info


@function_tool
async def analyze_bull_bear_spread(period: str) -> str:
    """Analyze AAII Bull-Bear Spread (investor sentiment indicator).
    
    Args:
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('aaii')
    data = await src.fetch_data('AAII_BULL_BEAR_SPREAD', period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    return f"""{period_name} AAII Bull-Bear Spread:
            - Start: {analysis['start']:+.2f}
            - End: {analysis['end']:+.2f}
            - Change: {analysis['change']:+.2f}
            - High: {analysis['high']:+.2f}
            - Low: {analysis['low']:+.2f}
            - Mean: {analysis['mean']:+.2f}"""


@function_tool
async def generate_bull_bear_spread_chart(period: str) -> str:
    """Generate AAII Bull-Bear Spread chart.
    
    Args:
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('aaii')
    data = await src.fetch_data('AAII_BULL_BEAR_SPREAD', period)
    actual_period = src.get_actual_period_approx(data)
    chart_info = await src.create_chart(
        data, 'AAII_BULL_BEAR_SPREAD', actual_period,
        label='AAII Bull-Bear Spread',
        ylabel='Bull-Bear Spread',
        value_format='{:.2f}',
        threshold_upper=None,
        threshold_lower=-0.2,
        overbought_label='Overbought Zone',
        oversold_label='Oversold Zone'
    )
    return chart_info


@function_tool
async def analyze_put_call(period: str) -> str:
    """Analyze CBOE Equity Put/Call Ratio.
    
    Args:
        period: Time period (5d, 1mo, 3mo, etc.)
    """
    src = get_data_source('ycharts')
    data = await src.fetch_data('CBOE_PUT_CALL_EQUITY', period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    return f"""{period_name} CBOE Equity Put/Call Ratio:
            - Start: {analysis['start']:.2f}
            - End: {analysis['end']:.2f}
            - Change: {analysis['change']:+.2f}
            - High: {analysis['high']:.2f}
            - Low: {analysis['low']:.2f}
            - Mean: {analysis['mean']:.2f}"""


@function_tool
async def generate_put_call_chart(period: str) -> str:
    """Generate CBOE Equity Put/Call Ratio chart.
    
    Args:
        period: Time period (5d, 1mo, 3mo, etc.)
    """
    src = get_data_source('ycharts')
    data = await src.fetch_data('CBOE_PUT_CALL_EQUITY', period)
    actual_period = src.get_actual_period_approx(data)
    chart_info = await src.create_chart(
        data, 'CBOE_PUT_CALL_EQUITY', actual_period,
        label='CBOE Equity Put/Call Ratio',
        ylabel='Put/Call Ratio',
        value_format='{:.2f}',
        threshold_upper=1.5,
        threshold_lower=0.5,
        overbought_label='Bearish Sentiment',
        oversold_label='Bullish Sentiment'
    )
    return chart_info


@function_tool
async def analyze_vix(period: str) -> str:
    """Analyze VIX (Volatility Index) - market fear gauge.
    
    Args:
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('yfinance')
    data = await src.fetch_data('^VIX', period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    return f"""{period_name} VIX (Volatility Index):
            - Start: {analysis['start']:.2f}
            - End: {analysis['end']:.2f}
            - Change: {analysis['change_pct']:+.2f}%
            - High: {analysis['high']:.2f}
            - Low: {analysis['low']:.2f}"""


@function_tool
async def generate_vix_chart(period: str) -> str:
    """Generate VIX (Volatility Index) chart.
    
    Args:
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
    """
    src = get_data_source('yfinance')
    data = await src.fetch_data('^VIX', period)
    actual_period = src.get_actual_period_approx(data)
    
    chart_info = await src.create_chart(
        data, '^VIX', actual_period,
        label='VIX (Volatility Index)',
        chart_type='line',
        ylabel='VIX Level',
        data_column='Close',
        value_format='{:.2f}',
        threshold_upper=30.0,
        threshold_lower=20.0,
        overbought_label='Extreme Fear',
        oversold_label='High Volatility'
    )
    return chart_info


@function_tool
async def analyze_high_yield_spread(period: str) -> str:
    """Analyze ICE BofA US High Yield Spread (credit risk indicator).
    
    Args:
        period: Time period (6mo, 1y, 5y, 10y, etc.)
    """
    src = get_data_source('fred')
    data = await src.fetch_data('BAMLH0A0HYM2', period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    
    return f"""{period_name} ICE BofA US High Yield Spread:
            - Start: {analysis['start']:.2f}%
            - End: {analysis['end']:.2f}%
            - Change: {analysis['change_pct']:+.2f}%
            - High: {analysis['high']:.2f}%
            - Low: {analysis['low']:.2f}%"""


@function_tool
async def generate_high_yield_spread_chart(period: str) -> str:
    """Generate ICE BofA US High Yield Spread chart.
    
    Args:
        period: Time period (6mo, 1y, 5y, 10y, etc.)
    """
    src = get_data_source('fred')
    data = await src.fetch_data('BAMLH0A0HYM2', period)
    actual_period = src.get_actual_period_approx(data)
    
    chart_info = await src.create_chart(
        data, 'BAMLH0A0HYM2', actual_period,
        label='ICE BofA US High Yield Spread',
        chart_type='line',
        baseline=5.0,
        positive_label='Alert Zone',
        negative_label='Complacent Zone'
    )

    return chart_info


@function_tool
async def analyze_margin_debt(symbol: str, period: str) -> str:
    """Analyze FINRA Margin Statistics (YoY change).
    
    Args:
        symbol: 'MARGIN_DEBT_YOY'
        period: Time period (6mo, 1y, 5y, max, etc.)
    """
    src = get_data_source('finra')
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    analysis = src.get_analysis(data, actual_period)
    period_name = get_period_name(actual_period)
    label = data.get('label', symbol)
    
    return f"""{period_name} {label}:
            - Start: {analysis['start']:.2f}
            - End: {analysis['end']:.2f}
            - Change: {analysis['change']:+.2f}
            - High: {analysis['high']:.2f}
            - Low: {analysis['low']:.2f}
            - Mean: {analysis['mean']:.2f}"""


@function_tool
async def generate_margin_debt_chart(symbol: str, period: str) -> str:
    """Generate FINRA Margin Statistics chart (YoY change).
    
    Args:
        symbol: 'MARGIN_DEBT_YOY'
        period: Time period (6mo, 1y, 5y, max, etc.)
    """
    src = get_data_source('finra')
    data = await src.fetch_data(symbol, period)
    actual_period = src.get_actual_period_approx(data)
    
    label = data.get('label', symbol)
    
    chart_info = await src.create_chart(
        data, symbol, actual_period,
        label=label,
        ylabel='Margin Debt (YoY Change %)',
        value_format='{:.2f}',
        threshold_upper=50.0,
        threshold_lower=-20.0,
        overbought_label='Extreme Leverage',
        oversold_label='Deleveraging'
    )
    return chart_info


@function_tool
async def generate_PE_PEG_ratio_chart(ticker: str, period: str = '10Y') -> str:
    """
    Generate P/E (NTM) and PEG (NTM) ratio charts with Historical Price overlay using Koyfin automation.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'NVDA', 'AAPL', 'MSFT')
        period: Chart period - '1Y', '3Y', '5Y', '10Y', '20Y' (default: '10Y')
    
    Returns:
        Chart path and metrics including:
        - P/E (NTM): current value, plus1_std, minus1_std
        - PEG (NTM): current value, plus1_std, minus1_std
        
        IMPORTANT: You MUST analyze BOTH P/E and PEG values in your response.
    
    Note:
        - Chart captures take ~12-15 seconds per ticker
        - For multiple tickers, consider using koyfin_parallel for faster execution
        - Chart saved to 'charts/{ticker}_Koyfin_ForwardPE.png'
    """

    # Run blocking Selenium code in thread pool to avoid blocking event loop
    def _capture():
        capturer = KoyfinChartCapture(headless=True, verbose=False)
        return capturer.capture(ticker, period=period.upper())
    
    chart_path, metrics = await asyncio.to_thread(_capture)
    
    if chart_path and metrics:
        # Parse metrics dict into clear format
        pe = metrics.get('pe', {})
        peg = metrics.get('peg', {})
        
        formatted_metrics = f"""
        P/E (NTM):
        - Current value: {pe.get('value')}
        - lowerbound: {pe.get('minus1_std')} (Undervalued)
        - upperbound: {pe.get('plus1_std')} (Overvalued)
        - Midpoint: {(pe.get('minus1_std') + pe.get('plus1_std')) / 2 
        if type(pe.get('minus1_std')) == float and type(pe.get('plus1_std')) == float else None}

        PEG (NTM):
        - Current value: {peg.get('value')}
        - lowerbound: {peg.get('minus1_std')} (Undervalued)
        - upperbound: {peg.get('plus1_std')} (Overvalued)
        - Midpoint: {(peg.get('minus1_std') + peg.get('plus1_std')) / 2
        if type(peg.get('minus1_std')) == float and type(peg.get('plus1_std')) == float else None}
        """.strip()
        
        return f"Chart saved: {chart_path}\n\n{formatted_metrics}"
    else:
        return f"Failed to capture P/E and PEG chart for {ticker}. Try with headless=False for better reliability."


@function_tool
async def analyze_market_pe(pe_type: str = 'trailing', period: str = '10y') -> str:
    """Analyze S&P 500 Market P/E ratio data from factset_report_analyzer.
    
    Args:
        pe_type: Type of P/E ratio - 'trailing' (default) or 'forward'
        period: Time period for analysis (1mo, 6mo, 1y, 2y, 5y, 10y)
    
    Returns:
        Analysis text with current, start, end, high, low, and percentile information
    """
    try:
        sp500 = SP500()
        sp500.set_type(pe_type)
        pe_df = sp500.pe_ratio.sort_values('Date')
        
        if pe_df.empty:
            return f"S&P 500 {pe_type} P/E ratio data not available"
        
        # Convert Date column to datetime if needed
        if not isinstance(pe_df['Date'].iloc[0], pd.Timestamp):
            pe_df['Date'] = pd.to_datetime(pe_df['Date'])
        
        pe_df = pe_df.set_index('Date')
        pe_series = pe_df['PE_Ratio']
        
        # Filter by period
        period_days = {
            '1mo': 30, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825, '10y': 3650
        }.get(period.lower(), 365)
        
        cutoff_date = datetime.now() - timedelta(days=period_days)
        filtered_pe = pe_series[pe_series.index >= cutoff_date]
        
        if filtered_pe.empty:
            filtered_pe = pe_series
        
        current_pe = float(filtered_pe.iloc[-1])
        start_pe = float(filtered_pe.iloc[0])
        end_pe = float(filtered_pe.iloc[-1])
        high_pe = float(filtered_pe.max())
        low_pe = float(filtered_pe.min())
        change_pct = ((current_pe - start_pe) / start_pe) * 100
        
        # Calculate percentile rank
        current_rank = float(filtered_pe.rank(pct=True).iloc[-1] * 100)
        
        # Calculate percentiles for thresholds
        upper_threshold = float(filtered_pe.quantile(0.80))
        lower_threshold = float(filtered_pe.quantile(0.20))
        
        period_name = {
            '1mo': '1 Month', '6mo': '6 Months', '1y': '1 Year',
            '2y': '2 Years', '5y': '5 Years', '10y': '10 Years'
        }.get(period.lower(), period)
        
        return f"""{period_name} S&P 500 {pe_type.capitalize()} P/E Ratio Analysis:
            - Current: {current_pe:.2f}
            - Change: {change_pct:+.2f}%
            - Start: {start_pe:.2f}
            - End: {end_pe:.2f}
            - High: {high_pe:.2f}
            - Low: {low_pe:.2f}
            - Current Rank: {current_rank:.1f}%
            - Overvalued threshold (80th percentile): {upper_threshold:.2f}
            - Undervalued threshold (20th percentile): {lower_threshold:.2f}"""
    
    except Exception as e:
        return f"Error analyzing market P/E ratio: {str(e)}"


@function_tool
async def generate_market_pe_chart(pe_type: str = 'trailing') -> str:
    """Generate S&P 500 Market P/E ratio chart from factset_report_analyzer.
    
    Args:
        pe_type: Type of P/E ratio - 'trailing' (default) or 'forward'
    
    Returns:
        Chart file path string
    """
    try:
        filepath = os.path.join(CHART_OUTPUT_DIR, f"S&P500_{pe_type}_PE_chart.png")

        # Get SP500 data
        sp500 = SP500()
        sp500.set_type(pe_type)
        pe_df = sp500.pe_ratio.sort_values('Date')

        # Plot single series with sigma highlighting
        plot_time_series(
            dates=pe_df['Date'],
            values=[pe_df['Price'], pe_df['PE_Ratio']],
            sigma=1.5,  # Highlight periods outside ±1.5σ
            sigma_index=1, # Apply sigma to P/E ratio (second series)
            labels=['S&P 500 Price', f'{pe_type.capitalize()} P/E Ratio'],
            colors=['black', 'green' if pe_type == 'trailing' else 'red'],
            output_path=filepath
        )
        
        return f"Chart saved: {filepath}"
    
    except Exception as e:
        return f"Error generating market P/E ratio chart: {str(e)}"
