import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from src.config import CHART_OUTPUT_DIR


def create_yfinance_chart(ticker: str, data, period: str, ylabel: str, value_format: str) -> str:
    """
    Create candlestick chart for yfinance data with SMA overlays.
    
    Args:
        ticker: Stock ticker symbol
        data: DataFrame with OHLCV data
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
        ylabel: Y-axis label
        value_format: Format string for values
        
    Returns:
        String with chart file path
    """
    if data.empty:
        return f"{ticker} data not available"

    # Period display names
    period_display = {
        "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
        "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
    }.get(period, period)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Candlestick plot using integer positions (no gaps for weekends)
    ohlc = data[['Open', 'High', 'Low', 'Close']]
    dates = data.index
    num_candles = len(ohlc)
    positions = range(num_candles)
    width = 0.6
    
    for i, (o, h, l, c) in enumerate(ohlc.values):
        color_candle = '#2ca02c' if c >= o else '#d62728'
        # Wick
        ax.vlines(i, l, h, color=color_candle, linewidth=1, zorder=2)
        # Body
        lower = min(o, c)
        height = abs(c - o)
        if height == 0:
            ax.hlines(o, i - width/2, i + width/2, color=color_candle, linewidth=2, zorder=3)
        else:
            ax.add_patch(Rectangle((i - width/2, lower), width, height, 
                                   facecolor=color_candle, edgecolor=color_candle, alpha=0.8, zorder=3))
    
    # Overlay SMAs
    try:
        sma_plotted = False
        period_lower = period.lower()
        show_5_20 = period_lower in ["1mo", "3mo", "6mo"]
        show_200 = period_lower in ["1y", "2y", "5y", "10y", "max"]
        
        if show_5_20 or show_200:
            if 'SMA_5' in data.columns and (show_5_20 or show_200):
                ax.plot(positions, data['SMA_5'], label='SMA 5', linewidth=1.2, color='#e377c2', 
                        alpha=0.9, linestyle='-', zorder=4)
                sma_plotted = True
            if 'SMA_20' in data.columns and (show_5_20 or show_200):
                ax.plot(positions, data['SMA_20'], label='SMA 20', linewidth=1.2, color='#8c564b', 
                        alpha=0.9, linestyle='-', zorder=4)
                sma_plotted = True
            if 'SMA_200' in data.columns and show_200:
                ax.plot(positions, data['SMA_200'], label='SMA 200', linewidth=2.0, color='#17becf', 
                        alpha=1.0, linestyle='-', zorder=5)
                sma_plotted = True
        
        if sma_plotted:
            ax.legend(loc='upper left', fontsize=9)
    except Exception:
        pass
    
    # X-axis: dates at integer positions
    ax.set_xlim(-0.5, num_candles - 0.5)
    tick_spacing = max(1, num_candles // 10)
    tick_positions = list(range(0, num_candles, tick_spacing))
    if tick_positions[-1] != num_candles - 1:
        tick_positions.append(num_candles - 1)
    tick_labels = [dates[i].strftime('%Y-%m-%d') if period not in ["5d", "1mo"] else dates[i].strftime('%m/%d') 
                   for i in tick_positions]
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    # Title and labels
    ax.set_title(f'{ticker} - {period_display}', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Value display
    close_values = data['Close']
    start_val = float(close_values.iloc[0])
    end_val = float(close_values.iloc[-1])
    change = ((end_val - start_val) / start_val) * 100 if start_val != 0 else 0
    change_color = 'green' if change < 0 else 'red'
    
    ax.text(0.02, 0.95, f'Start: {value_format.format(start_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.85, f'End: {value_format.format(end_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.75, f'Change: {change:+.2f}%', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=change_color, alpha=0.3))
    
    plt.tight_layout()
    
    # Save chart
    ticker_clean = ticker.replace('^', '').replace('-', '_')
    filename = f"{ticker_clean}_{period}_chart.png"
    filepath = os.path.join(CHART_OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}"


def create_fred_chart(
    data, 
    indicator_name: str,
    period: str = "6mo",
    baseline: float = None,
    positive_label: str = "Above Baseline",
    negative_label: str = "Below Baseline"
) -> str:
    """
    Create line chart for FRED economic data with baseline.
    
    Args:
        data: Pandas Series with economic data
        indicator_name: Name of the indicator
        period: Time period (5d, 1mo, 6mo, 1y, etc.)
        baseline: Optional baseline value (e.g., 0 for NFCI)
        positive_label: Label for values above baseline
        negative_label: Label for values below baseline
        
    Returns:
        String with chart file path
    """
    if data.empty:
        return f"{indicator_name} data not available"
    
    values = data.values
    dates = data.index
    
    # Period display names
    period_display = {
        "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
        "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
    }.get(period, period)
    
    # Color scheme
    colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c", "1y": "#d62728", "2y": "#9467bd"}
    color = colors.get(period, "#1f77b4")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Line plot
    ax.plot(dates, values, linewidth=2, color=color, marker='o', markersize=3, zorder=2)
    ax.fill_between(dates, values, alpha=0.15, color=color, zorder=1)
    
    # Add baseline if provided
    if baseline is not None:
        ax.axhline(y=baseline, color='black', linestyle='--', linewidth=1, alpha=0.5, 
                   label=f'Baseline ({baseline})')
        
        # Shade positive/negative regions
        ax.fill_between(dates, baseline, values, 
                         where=(values >= baseline), color='red', alpha=0.1, label=positive_label)
        ax.fill_between(dates, baseline, values, 
                         where=(values < baseline), color='green', alpha=0.1, label=negative_label)
        ax.legend(loc='upper left', fontsize=9)
    
    # Title and labels
    ax.set_title(f'{indicator_name} - {period_display}', fontsize=13, fontweight='bold')
    ax.set_ylabel(f'{indicator_name} Value', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Value display
    start_val = values[0]
    end_val = values[-1]
    
    if baseline is not None:
        # FRED style: latest value with condition
        latest_date = dates[-1].strftime('%Y-%m-%d')
        condition = positive_label if end_val >= baseline else negative_label
        box_color = '#ffcccc' if end_val >= baseline else '#ccffcc'
        
        ax.text(0.02, 0.95, f'Latest ({latest_date}): {end_val:.3f}', 
                transform=ax.transAxes, verticalalignment='top', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.7))
        
        if condition:
            ax.text(0.02, 0.85, condition, transform=ax.transAxes, 
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Date formatting
    if period in ["5d", "1mo"]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save chart
    indicator_clean = indicator_name.replace(' ', '_').replace('(', '').replace(')', '')
    filename = f"{indicator_clean}_{period}_chart.png"
    filepath = os.path.join(CHART_OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}"


def create_line_chart(
    data,
    title: str,
    ylabel: str,
    period: str = "1y",
    value_format: str = "{:.2f}",
    baseline: float = None,
    positive_label: str = "Above Baseline",
    negative_label: str = "Below Baseline",
    data_column: str = None
) -> str:
    """
    Create generic line chart (for disparity, RSI, etc.).
    
    Args:
        data: DataFrame or Series
        title: Chart title
        ylabel: Y-axis label
        period: Time period
        value_format: Format string for values
        baseline: Optional baseline value
        positive_label: Label for values above baseline
        negative_label: Label for values below baseline
        data_column: Column name if DataFrame
        
    Returns:
        String with chart file path
    """
    if data.empty:
        return f"{title} data not available"
    
    # Handle different data types
    if hasattr(data, 'columns') and data_column:
        values = data[data_column]
        dates = data.index
    else:
        values = data.values if hasattr(data, 'values') else data
        dates = data.index
    
    # Period display names
    period_display = {
        "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
        "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
    }.get(period, period)
    
    colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c", "1y": "#d62728", "2y": "#9467bd"}
    color = colors.get(period, "#1f77b4")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Line plot
    ax.plot(dates, values, linewidth=2, color=color, marker='o', markersize=3, zorder=2)
    ax.fill_between(dates, values, alpha=0.15, color=color, zorder=1)
    
    # Add baseline if provided
    if baseline is not None:
        ax.axhline(y=baseline, color='black', linestyle='--', linewidth=1, alpha=0.5, 
                   label=f'Baseline ({baseline})')
        
        # Shade positive/negative regions
        ax.fill_between(dates, baseline, values, 
                         where=(values >= baseline), color='red', alpha=0.1, label=positive_label)
        ax.fill_between(dates, baseline, values, 
                         where=(values < baseline), color='green', alpha=0.1, label=negative_label)
        ax.legend(loc='upper left', fontsize=9)
    
    # Title and labels
    ax.set_title(f'{title} - {period_display}', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Date formatting
    if period in ["5d", "1mo"]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    else:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Save chart
    title_clean = title.replace('^', '').replace('-', '_').replace(' ', '_').replace('(', '').replace(')', '')
    filename = f"{title_clean}_{period}_chart.png"
    filepath = os.path.join(CHART_OUTPUT_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}"
