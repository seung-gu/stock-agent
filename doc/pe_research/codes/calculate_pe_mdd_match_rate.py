"""
Calculate match rate: MDD local minima within 3 days of P/E -1.5σ periods.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from scipy.signal import find_peaks
from datetime import datetime

# P/E definitions mapping
PE_DEFINITIONS = {
    'Mixed Operating': {
        'file': 'pe_q0_to_q3_results.csv',
        'label': 'Mixed Operating [Q(0)+Q\'(1)+Q\'(2)+Q\'(3)]'
    },
    'Trailing-like Operating': {
        'file': 'pe_qm3_to_q0_results.csv',
        'label': 'Trailing-like Operating [Q(-3)+Q(-2)+Q(-1)+Q(0)]'
    },
    'Forward Operating': {
        'file': 'pe_q1_to_q4_results.csv',
        'label': 'Forward Operating [Q\'(1)+Q\'(2)+Q\'(3)+Q\'(4)]'
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


def find_mdd_bottoms_in_drawdown_periods(price_series, drawdown_series, threshold=-8.0):
    """
    Find MDD local minima: deepest drawdown in each period from MDD < threshold to next new high.
    """
    # Find periods where MDD < threshold
    below_threshold = drawdown_series[drawdown_series < threshold]
    
    if len(below_threshold) == 0:
        return pd.DataFrame(columns=['date', 'drawdown', 'is_bottom'])
    
    # Find new highs (when price exceeds previous rolling max, MDD resets to 0)
    rolling_max = price_series.expanding(min_periods=1).max()
    new_highs_mask = price_series >= rolling_max.shift(1).fillna(price_series.iloc[0])
    new_high_dates = price_series[new_highs_mask].index.tolist()
    
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


def calculate_match_rate(mdd_bottoms, sigma_periods, window_days=3):
    """
    Calculate match rate: how many sigma periods have MDD bottom within window_days.
    
    Returns:
        Dictionary with match statistics
    """
    if len(mdd_bottoms) == 0:
        return {
            'sigma_period_count': len(sigma_periods),
            'mdd_bottom_count': 0,
            'periods_with_mdd': 0,
            'match_rate': 0.0
        }
    
    if len(sigma_periods) == 0:
        return {
            'sigma_period_count': 0,
            'mdd_bottom_count': len(mdd_bottoms),
            'periods_with_mdd': 0,
            'match_rate': 0.0
        }
    
    # Check each sigma period
    periods_with_mdd = 0
    
    for _, sigma_row in sigma_periods.iterrows():
        start = sigma_row['start_date']
        end = sigma_row['end_date']
        
        # Expand period by window_days on both sides
        expanded_start = start - pd.Timedelta(days=window_days)
        expanded_end = end + pd.Timedelta(days=window_days)
        
        # Check if any MDD bottom falls within expanded period
        for _, bottom_row in mdd_bottoms.iterrows():
            bottom_date = bottom_row['date']
            if expanded_start <= bottom_date <= expanded_end:
                periods_with_mdd += 1
                break
    
    match_rate = (periods_with_mdd / len(sigma_periods) * 100) if len(sigma_periods) > 0 else 0.0
    
    return {
        'sigma_period_count': len(sigma_periods),
        'mdd_bottom_count': len(mdd_bottoms),
        'periods_with_mdd': periods_with_mdd,
        'match_rate': match_rate
    }


def main():
    """Main analysis function."""
    print("Loading S&P 500 price data...")
    price_series = load_price_data()
    
    print("Calculating MDD...")
    drawdown_series = calculate_mdd(price_series)
    
    print("Finding MDD bottoms in periods < -8% before next new high...")
    mdd_bottoms = find_mdd_bottoms_in_drawdown_periods(price_series, drawdown_series, threshold=-8.0)
    print(f"Found {len(mdd_bottoms)} MDD local minima")
    if len(mdd_bottoms) > 0:
        print("MDD bottoms:")
        for _, row in mdd_bottoms.iterrows():
            print(f"  {row['date'].date()}: {row['drawdown']:.2f}%")
    
    # Analyze each P/E definition
    results = []
    
    print("\n" + "="*80)
    print("MATCH RATE ANALYSIS: MDD Bottoms within 3 days of P/E -1.5σ periods")
    print("="*80)
    
    for pe_name, pe_config in PE_DEFINITIONS.items():
        print(f"\n{pe_name}:")
        try:
            # Load P/E data
            pe_file = f"doc/pe_research/{pe_config['file']}"
            pe_series = load_pe_data(pe_file)
            
            # Find -1.5σ periods
            sigma_periods = find_sigma_periods(pe_series, sigma_multiplier=-1.5)
            print(f"  -1.5σ periods: {len(sigma_periods)}")
            
            # Calculate match rate
            match_stats = calculate_match_rate(mdd_bottoms, sigma_periods, window_days=3)
            
            print(f"  MDD bottoms: {match_stats['mdd_bottom_count']}")
            print(f"  Periods with MDD bottom within ±3 days: {match_stats['periods_with_mdd']}")
            print(f"  Match rate: {match_stats['match_rate']:.1f}%")
            
            match_stats['pe_name'] = pe_name
            match_stats['pe_label'] = pe_config['label']
            results.append(match_stats)
            
        except FileNotFoundError:
            print(f"  Warning: File {pe_config['file']} not found, skipping...")
        except Exception as e:
            print(f"  Error analyzing {pe_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Create summary table
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    
    summary_df = pd.DataFrame(results)
    if len(summary_df) > 0:
        cols = ['pe_name', 'sigma_period_count', 'mdd_bottom_count', 'periods_with_mdd', 'match_rate']
        summary_df = summary_df[cols]
        
        print(summary_df.to_string(index=False))
        
        # Save to CSV
        output_file = "doc/pe_research/pe_mdd_match_rate_analysis.csv"
        summary_df.to_csv(output_file, index=False)
        print(f"\nResults saved to {output_file}")
    
    return summary_df


if __name__ == "__main__":
    summary_df = main()

