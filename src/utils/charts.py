import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile

# Create temp directory for charts
TEMP_CHART_DIR = tempfile.mkdtemp(prefix="market_charts_")


def create_chart(
    data, 
    title: str, 
    ylabel: str, 
    period: str = "6mo",
    value_format: str = "{:.2f}",
    baseline: float = None,
    positive_label: str = "Above Baseline",
    negative_label: str = "Below Baseline",
    data_column: str = None
) -> str:
    """
    Unified chart creation function for both yfinance and FRED data.
    
    Args:
        data: Pandas DataFrame (yfinance) or Series (FRED)
        title: Chart title
        ylabel: Y-axis label
        period: Time period (5d, 1mo, 6mo, etc.)
        value_format: Format string for values
        baseline: Optional baseline value (for FRED indicators)
        positive_label: Label for values above baseline
        negative_label: Label for values below baseline
        data_column: Column name for yfinance data (default: 'Close')
        
    Returns:
        Formatted string with chart path for markdown link
    """
    if data.empty:
        return f"{title} data not available"
    
    # Handle different data types
    if hasattr(data, 'columns') and data_column:
        # yfinance DataFrame
        values = data[data_column]
        dates = data.index
    else:
        # FRED Series
        values = data.values
        dates = data.index
    
    # Period display names
    period_display = {
        "5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months",
        "1y": "1 Year", "2y": "2 Years"
    }.get(period, period)
    
    # Color scheme
    colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c", "1y": "#d62728", "2y": "#9467bd"}
    color = colors.get(period, "#1f77b4")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    
    # Plot main line
    ax.plot(dates, values, linewidth=2, color=color, marker='o', markersize=3)
    ax.fill_between(dates, values, alpha=0.3, color=color)
    
    # Add baseline if provided (FRED indicators)
    if baseline is not None:
        ax.axhline(y=baseline, color='black', linestyle='--', linewidth=1, alpha=0.5, 
                   label=f'Baseline ({baseline})')
        
        # Shade positive/negative regions
        ax.fill_between(dates, baseline, values, 
                         where=(values >= baseline), color='red', alpha=0.1, label=positive_label)
        ax.fill_between(dates, baseline, values, 
                         where=(values < baseline), color='green', alpha=0.1, label=negative_label)
        ax.legend(loc='upper left', fontsize=9)
    
    ax.set_title(f'{title} - {period_display}', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Display values
    start_val = values.iloc[0] if hasattr(values, 'iloc') else values[0]
    end_val = values.iloc[-1] if hasattr(values, 'iloc') else values[-1]
    change = ((end_val - start_val) / start_val) * 100 if start_val != 0 else 0
    
    # Value display
    if baseline is not None:
        # FRED style: latest value with condition
        latest_date = dates[-1].strftime('%Y-%m-%d')
        condition = positive_label if end_val >= baseline else negative_label
        box_color = '#ffcccc' if end_val >= baseline else '#ccffcc'
        
        ax.text(0.02, 0.95, f'Latest ({latest_date}): {value_format.format(end_val)}', 
                transform=ax.transAxes, verticalalignment='top', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=box_color, alpha=0.7))
        
        if condition:
            ax.text(0.02, 0.85, condition, transform=ax.transAxes, 
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    else:
        # yfinance style: start/end/change
        change_color = 'green' if change < 0 else 'red'
        ax.text(0.02, 0.95, f'Start: {value_format.format(start_val)}', transform=ax.transAxes, 
                verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(0.02, 0.85, f'End: {value_format.format(end_val)}', transform=ax.transAxes, 
                verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        ax.text(0.02, 0.75, f'Change: {change:+.2f}%', transform=ax.transAxes, 
                verticalalignment='top', fontsize=10, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor=change_color, alpha=0.3))
    
    # Set Y-axis limits
    y_min = float(values.min())
    y_max = float(values.max())
    span = y_max - y_min
    padding = max(abs(y_min) * 0.01, 0.05) if span == 0 else span * 0.10
    ax.set_ylim(y_min - padding, y_max + padding)
    
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
    filepath = os.path.join(TEMP_CHART_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}\n\nIMPORTANT: Copy this EXACT path to create markdown link: [View Chart](sandbox:{filepath})"


# Convenience functions for backward compatibility
def create_yfinance_chart(ticker: str, data, period: str, ylabel: str, value_format: str) -> str:
    """Backward compatibility wrapper for yfinance charts."""
    return create_chart(
        data=data,
        title=ticker,
        ylabel=ylabel,
        period=period,
        value_format=value_format,
        data_column='Close'
    )


def create_fred_chart(
    data, 
    indicator_name: str,
    period: str = "6mo",
    baseline: float = None,
    positive_label: str = "Above Baseline",
    negative_label: str = "Below Baseline"
) -> str:
    """Backward compatibility wrapper for FRED charts."""
    return create_chart(
        data=data,
        title=indicator_name,
        ylabel=f'{indicator_name} Value',
        period=period,
        value_format='{:.3f}',
        baseline=baseline,
        positive_label=positive_label,
        negative_label=negative_label
    )
