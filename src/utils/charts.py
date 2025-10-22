import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile

# Create temp directory for charts
TEMP_CHART_DIR = tempfile.mkdtemp(prefix="market_charts_")


def create_single_chart(ticker: str, data, period: str, ylabel: str, value_format: str) -> str:
    """
    Create a single trend chart for the given ticker and period.
    
    Args:
        ticker: Ticker symbol (e.g., "^TNX")
        data: Historical price data from yfinance
        period: Period options: 5d, 1mo, 6mo
        ylabel: Y-axis label (e.g., "Price ($)", "Yield (%)")
        value_format: Format string for values (e.g., "${:.2f}", "{:.2f}%")
        
    Returns:
        Filename of the saved chart or None if data is empty
    """
    if data.empty:
        return None
    
    period_name = {"5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months"}.get(period, period)
    colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c"}
    color = colors.get(period, "#1f77b4")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], linewidth=2, color=color, marker='o', markersize=4)
    ax.fill_between(data.index, data['Close'], alpha=0.3, color=color)
    ax.set_title(f'{ticker} {period_name} Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Display start/end values
    start_val = data['Close'].iloc[0]
    end_val = data['Close'].iloc[-1]
    change = ((end_val - start_val) / start_val) * 100
    
    change_color = 'green' if change < 0 else 'red'
    ax.text(0.02, 0.95, f'Start: {value_format.format(start_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.85, f'End: {value_format.format(end_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.75, f'Change: {change:+.2f}%', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=change_color, alpha=0.3))
    
    # Set Y-axis limits dynamically based on data range
    y_min = float(data['Close'].min())
    y_max = float(data['Close'].max())
    span = y_max - y_min
    padding = max(abs(y_min) * 0.01, 0.05) if span == 0 else span * 0.10
    ax.set_ylim(y_min - padding, y_max + padding)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart to temp directory
    ticker_clean = ticker.replace('^', '').replace('-', '_')
    filename = f"{ticker_clean}_{period_name.lower().replace(' ', '_')}_chart.png"
    filepath = os.path.join(TEMP_CHART_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}\n\nIMPORTANT: Copy this EXACT path to create markdown link: [View Chart](sandbox:{filepath})"
