"""
Visualize MDD bottoms and P/E -1.5σ periods alignment.

Creates charts showing:
1. MDD bottoms (local minima) marked on price chart
2. P/E -1.5σ periods highlighted
3. Alignment visualization
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.signal import find_peaks
from datetime import datetime

# P/E definitions mapping
PE_DEFINITIONS = {
    'Mixed Operating': {
        'file': 'pe_q0_to_q3_results.csv',
        'label': 'Mixed Operating [Q(0)+Q\'(1)+Q\'(2)+Q\'(3)]',
        'color': '#2E86AB'
    },
    'Trailing-like Operating': {
        'file': 'pe_qm3_to_q0_results.csv',
        'label': 'Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)]',
        'color': '#A23B72'
    },
    'Forward Operating': {
        'file': 'pe_q1_to_q4_results.csv',
        'label': 'Forward Operating [Q\'(1)+Q\'(2)+Q\'(3)+Q\'(4)]',
        'color': '#F18F01'
    }
}


def load_price_data():
    """Load S&P 500 price data."""
    ticker = yf.Ticker("^GSPC")
    df = ticker.history(start="2016-12-01", end="2025-12-01")
    df.index = df.index.tz_localize(None)
    return df['Close']


def calculate_mdd(price_series):
    """Calculate current drawdown from most recent peak."""
    rolling_max = price_series.expanding(min_periods=1).max()
    drawdown = (price_series - rolling_max) / rolling_max * 100
    return drawdown


def find_mdd_bottoms_in_drawdown_periods(price_series, drawdown_series, min_distance_days=30, threshold=-8.0):
    """
    Find MDD local minima only in periods where MDD < threshold (more negative than -8%) and before next new high.
    
    Args:
        price_series: Price series to detect new highs
        drawdown_series: Drawdown series
        min_distance_days: Minimum distance between bottoms in days
        threshold: MDD threshold (default: -8%, meaning MDD must be more negative than -8%)
    
    Returns:
        DataFrame with columns: date, drawdown, is_bottom
    """
    # Find periods where MDD < threshold (more negative than -8%)
    below_threshold = drawdown_series[drawdown_series < threshold]
    
    if len(below_threshold) == 0:
        return pd.DataFrame(columns=['date', 'drawdown', 'is_bottom'])
    
    # Find new highs (when price exceeds previous rolling max, MDD resets to 0)
    rolling_max = price_series.expanding(min_periods=1).max()
    new_highs_mask = price_series >= rolling_max.shift(1).fillna(price_series.iloc[0])
    new_high_dates = price_series[new_highs_mask].index.tolist()
    
    if len(below_threshold) == 0:
        return pd.DataFrame(columns=['date', 'drawdown', 'is_bottom'])
    
    # Group by new high cycles: from one new high to the next
    periods = []
    
    # Find periods: from start of MDD < -8% to next new high (when MDD resets to 0)
    i = 0
    while i < len(below_threshold):
        start_date = below_threshold.index[i]
        
        # Find the next new high after this date
        next_highs = [d for d in new_high_dates if d > start_date]
        if len(next_highs) > 0:
            end_date = next_highs[0]
        else:
            end_date = drawdown_series.index[-1]
        
        # Find all dates in this period that are below threshold
        period_dates = below_threshold[(below_threshold.index >= start_date) & (below_threshold.index < end_date)]
        
        if len(period_dates) > 0:
            periods.append((start_date, end_date))
            # Move to next period (skip all dates before end_date)
            i = len(below_threshold[below_threshold.index < end_date])
        else:
            i += 1
    
    # Find the deepest drawdown (minimum) within each period
    all_bottoms = []
    
    for start_date, end_date in periods:
        # Get drawdown data for this period
        period_dd = drawdown_series[(drawdown_series.index >= start_date) & (drawdown_series.index <= end_date)]
        
        # Only consider data that is actually below threshold
        period_dd_below = period_dd[period_dd < threshold]
        
        if len(period_dd_below) == 0:
            continue
        
        # Find the deepest drawdown (minimum value) in this period
        min_idx = period_dd_below.idxmin()
        min_value = period_dd_below.min()
        
        # Only include if actually below threshold
        if min_value < threshold:
            all_bottoms.append({
                'date': min_idx,
                'drawdown': min_value,
                'is_bottom': True
            })
    
    if len(all_bottoms) == 0:
        return pd.DataFrame(columns=['date', 'drawdown', 'is_bottom'])
    
    return pd.DataFrame(all_bottoms)


def load_pe_data(filepath):
    """Load P/E data from CSV."""
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df['pe']


def find_sigma_periods(pe_series, sigma_multiplier=-1.5):
    """Find periods where P/E is below -1.5σ."""
    mean_pe = pe_series.mean()
    std_pe = pe_series.std()
    threshold = mean_pe + sigma_multiplier * std_pe
    
    # Find dates below threshold
    below_threshold = pe_series[pe_series <= threshold]
    
    if len(below_threshold) == 0:
        return pd.DataFrame(columns=['start_date', 'end_date', 'duration_days'])
    
    # Find continuous intervals
    intervals = []
    current_start = below_threshold.index[0]
    
    for i in range(1, len(below_threshold)):
        prev_date = below_threshold.index[i-1]
        curr_date = below_threshold.index[i]
        
        # If gap is more than 1 day, end current interval
        if (curr_date - prev_date).days > 1:
            intervals.append({
                'start_date': current_start,
                'end_date': prev_date,
                'duration_days': (prev_date - current_start).days + 1
            })
            current_start = curr_date
    
    # Add final interval
    intervals.append({
        'start_date': current_start,
        'end_date': below_threshold.index[-1],
        'duration_days': (below_threshold.index[-1] - current_start).days + 1
    })
    
    return pd.DataFrame(intervals)


def create_alignment_chart(price_series, drawdown_series, mdd_bottoms, pe_series, sigma_periods, pe_name, pe_config, output_file):
    """Create chart showing price, MDD, MDD bottoms, P/E, and -1.5σ periods."""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    
    # Plot 1: Price with MDD bottoms
    ax1.plot(price_series.index, price_series.values, 'k-', linewidth=1.5, label='S&P 500 Price', alpha=0.8)
    
    # Mark MDD bottoms
    if len(mdd_bottoms) > 0:
        all_prices = price_series.loc[mdd_bottoms['date']]
        ax1.scatter(mdd_bottoms['date'], all_prices.values, 
                    c='red', s=80, marker='v', alpha=0.8, label=f'MDD Local Minima ({len(mdd_bottoms)})', zorder=5)
    
    ax1.set_ylabel('S&P 500 Price', fontsize=12, fontweight='bold')
    ax1.set_title('S&P 500 Price with MDD Local Minima', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: MDD with bottoms marked
    ax2.plot(drawdown_series.index, drawdown_series.values, 'b-', linewidth=1.5, label='MDD', alpha=0.8)
    ax2.axhline(y=-8.0, color='orange', linestyle='--', linewidth=1, alpha=0.7, label='-8% Threshold')
    
    # Highlight periods below -8% (more negative than -8%)
    below_threshold = drawdown_series[drawdown_series < -8.0]
    if len(below_threshold) > 0:
        # Find continuous intervals
        intervals = []
        current_start = below_threshold.index[0]
        for i in range(1, len(below_threshold)):
            if (below_threshold.index[i] - below_threshold.index[i-1]).days > 1:
                intervals.append((current_start, below_threshold.index[i-1]))
                current_start = below_threshold.index[i]
        intervals.append((current_start, below_threshold.index[-1]))
        
        for start, end in intervals:
            ax2.axvspan(start, end, color='red', alpha=0.1, zorder=1)
    
    # Mark MDD bottoms on MDD chart
    if len(mdd_bottoms) > 0:
        bottom_dd = drawdown_series.loc[mdd_bottoms['date']]
        ax2.scatter(mdd_bottoms['date'], bottom_dd.values, 
                    c='red', s=100, marker='v', alpha=0.9, label=f'Local Minima ({len(mdd_bottoms)})', zorder=5)
    
    ax2.set_ylabel('MDD (%)', fontsize=12, fontweight='bold')
    ax2.set_title('MDD with Local Minima (in periods < -8% before next new high)', fontsize=14, fontweight='bold')
    ax2.legend(loc='lower left', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.invert_yaxis()  # Invert so negative values go down
    
    # Plot 3: P/E with -1.5σ periods
    ax3.plot(pe_series.index, pe_series.values, color=pe_config['color'], linewidth=1.5, 
             label=pe_config['label'], alpha=0.8)
    
    # Calculate sigma bands
    mean_pe = pe_series.mean()
    std_pe = pe_series.std()
    upper_bound = mean_pe + 1.5 * std_pe
    lower_bound = mean_pe - 1.5 * std_pe
    
    # Highlight -1.5σ periods
    for _, row in sigma_periods.iterrows():
        ax3.axvspan(row['start_date'], row['end_date'], color='blue', alpha=0.2, zorder=1)
    
    # Mark MDD bottoms on P/E chart (only if date exists in P/E series)
    if len(mdd_bottoms) > 0:
        bottoms_in_pe = mdd_bottoms[mdd_bottoms['date'].isin(pe_series.index)]
        if len(bottoms_in_pe) > 0:
            bottom_pe = pe_series.loc[bottoms_in_pe['date']]
            ax3.scatter(bottoms_in_pe['date'], bottom_pe.values, 
                        c='red', s=80, marker='v', alpha=0.8, zorder=5)
    
    # Draw sigma lines
    ax3.axhline(y=upper_bound, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='+1.5σ')
    ax3.axhline(y=lower_bound, color='gray', linestyle=':', linewidth=1, alpha=0.5, label='-1.5σ')
    ax3.axhline(y=mean_pe, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='Mean')
    
    ax3.set_ylabel('P/E Ratio', fontsize=12, fontweight='bold', color=pe_config['color'])
    ax3.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax3.set_title(f'{pe_config["label"]} with -1.5σ Periods and MDD Bottoms', fontsize=14, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=10)
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='y', labelcolor=pe_config['color'])
    
    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax3.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.setp(ax3.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")
    plt.close()


def main():
    """Main visualization function."""
    print("Loading S&P 500 price data...")
    price_series = load_price_data()
    
    print("Calculating MDD...")
    drawdown_series = calculate_mdd(price_series)
    
    print("Finding MDD bottoms in periods < -8% before next new high...")
    mdd_bottoms = find_mdd_bottoms_in_drawdown_periods(price_series, drawdown_series, min_distance_days=30, threshold=-8.0)
    print(f"Found {len(mdd_bottoms)} local minima in drawdown periods")
    
    # Create charts for each P/E definition
    for pe_name, pe_config in PE_DEFINITIONS.items():
        print(f"\nProcessing {pe_name}...")
        try:
            pe_file = f"doc/pe_research/{pe_config['file']}"
            pe_series = load_pe_data(pe_file)
            
            # Find -1.5σ periods
            sigma_periods = find_sigma_periods(pe_series, sigma_multiplier=-1.5)
            print(f"Found {len(sigma_periods)} -1.5σ periods")
            
            # Create chart
            output_file = f"doc/pe_research/mdd_alignment_{pe_name.lower().replace(' ', '_').replace('-', '_')}.png"
            create_alignment_chart(price_series, drawdown_series, mdd_bottoms, pe_series, sigma_periods, pe_name, pe_config, output_file)
            
        except FileNotFoundError:
            print(f"  Warning: File {pe_config['file']} not found, skipping...")
        except Exception as e:
            print(f"  Error processing {pe_name}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()

