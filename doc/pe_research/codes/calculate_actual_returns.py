"""Calculate actual average returns by P/E groups (with magnitude weighting)."""

import pandas as pd
import yfinance as yf
import numpy as np
from pathlib import Path


def main():
    # 1. Get S&P 500 Price data
    print("Fetching S&P 500 Price data...")
    sp500 = yf.Ticker("^GSPC")
    price_df = sp500.history(period="max")
    price_df.index = price_df.index.tz_localize(None)
    
    # 2. Load quarterly EPS (I, J, K, L, M)
    print("Loading quarterly EPS data...")
    excel_path = Path.home() / 'Downloads' / 'sp-500-eps-est.xlsx'
    df = pd.read_excel(excel_path, sheet_name='ESTIMATES&PEs', engine='openpyxl')
    
    start_row = 127
    end_row = 277
    
    dates_raw = df.iloc[start_row:end_row+1, 0].values
    col_i = df.iloc[start_row:end_row+1, 8].values
    col_j = df.iloc[start_row:end_row+1, 9].values
    col_k = df.iloc[start_row:end_row+1, 10].values
    col_l = df.iloc[start_row:end_row+1, 11].values
    col_m = df.iloc[start_row:end_row+1, 12].values
    
    data_list = []
    for date_val, i_val, j_val, k_val, l_val, m_val in zip(dates_raw, col_i, col_j, col_k, col_l, col_m):
        if pd.notna(date_val):
            try:
                date_str = str(date_val).split('(')[0].strip()
                date_parsed = pd.to_datetime(date_str)
                row_data = {'Date': date_parsed}
                if pd.notna(i_val):
                    row_data['I'] = float(i_val)
                if pd.notna(j_val):
                    row_data['J'] = float(j_val)
                if pd.notna(k_val):
                    row_data['K'] = float(k_val)
                if pd.notna(l_val):
                    row_data['L'] = float(l_val)
                if pd.notna(m_val):
                    row_data['M'] = float(m_val)
                data_list.append(row_data)
            except:
                pass
    
    quarterly_df = pd.DataFrame(data_list).set_index('Date').sort_index()
    
    # 3. Get Price at each quarter-end (2-week average)
    quarterly_prices = []
    for q_date in quarterly_df.index:
        start_window = q_date - pd.Timedelta(days=7)
        end_window = q_date + pd.Timedelta(days=7)
        
        mask = (price_df.index >= start_window) & (price_df.index <= end_window)
        window_prices = price_df.loc[mask, 'Close']
        
        if len(window_prices) > 0:
            avg_price = window_prices.mean()
            quarterly_prices.append(avg_price)
        else:
            price_dates = price_df.index[price_df.index >= q_date]
            if len(price_dates) > 0:
                closest_date = price_dates[0]
                quarterly_prices.append(price_df.loc[closest_date, 'Close'])
            else:
                quarterly_prices.append(None)
    
    quarterly_df['Price'] = quarterly_prices
    quarterly_df = quarterly_df[quarterly_df['Price'].notna()].copy()
    
    # 4. Calculate future returns
    for n_quarters in [1, 2, 3, 4]:
        quarterly_df[f'Return_{n_quarters}Q'] = quarterly_df['Price'].pct_change(n_quarters).shift(-n_quarters) * 100
    
    # 5. Analyze each EPS column with ACTUAL RETURNS
    eps_columns = ['I', 'J', 'K', 'L', 'M']
    eps_labels = {
        'I': 'Forward I',
        'J': 'Trailing (TTM)',
        'K': 'Forward K',
        'L': 'Forward L',
        'M': 'Forward M'
    }
    
    print("\n" + "="*110)
    print("AVERAGE RETURNS BY P/E GROUPS (Magnitude-Weighted Analysis)")
    print("="*110)
    
    summary_results = {}
    
    for eps_col in eps_columns:
        if eps_col not in quarterly_df.columns:
            continue
        
        valid_data = quarterly_df[quarterly_df[eps_col].notna()].copy()
        valid_data[f'PE_{eps_col}'] = valid_data['Price'] / valid_data[eps_col]
        
        mean_pe = valid_data[f'PE_{eps_col}'].mean()
        std_pe = valid_data[f'PE_{eps_col}'].std()
        valid_data[f'Zscore_{eps_col}'] = (valid_data[f'PE_{eps_col}'] - mean_pe) / std_pe
        
        print(f"\n{'='*110}")
        print(f"📊 {eps_labels[eps_col]} (Column {eps_col})")
        print(f"{'='*110}")
        
        summary_results[eps_col] = {}
        
        for n_quarters in [1, 2, 3, 4]:
            return_col = f'Return_{n_quarters}Q'
            
            valid_mask = valid_data[f'Zscore_{eps_col}'].notna() & valid_data[return_col].notna()
            zscore = valid_data[f'Zscore_{eps_col}'][valid_mask]
            returns = valid_data[return_col][valid_mask]
            
            if len(zscore) < 10:
                continue
            
            # Split into High P/E and Low P/E groups
            high_pe_returns = returns[zscore > 0]
            low_pe_returns = returns[zscore < 0]
            
            # Calculate average returns for each group
            avg_high_pe = high_pe_returns.mean()
            avg_low_pe = low_pe_returns.mean()
            difference = avg_low_pe - avg_high_pe
            
            # Calculate median for reference
            median_high_pe = high_pe_returns.median()
            median_low_pe = low_pe_returns.median()
            
            # Calculate standard deviation
            std_high_pe = high_pe_returns.std()
            std_low_pe = low_pe_returns.std()
            
            # Store results
            summary_results[eps_col][f'{n_quarters}Q'] = {
                'avg_high': avg_high_pe,
                'avg_low': avg_low_pe,
                'diff': difference,
                'n_high': len(high_pe_returns),
                'n_low': len(low_pe_returns)
            }
            
            # Calculate correlation for reference
            corr = zscore.corr(returns)
            
            print(f"\n{n_quarters}Q Forward ({n_quarters*3} months) - Correlation: {corr:+.3f}")
            print(f"  High P/E (Z>0): n={len(high_pe_returns):<3}  Avg={avg_high_pe:+6.2f}%  Median={median_high_pe:+6.2f}%  Std={std_high_pe:5.2f}%")
            print(f"  Low P/E (Z<0):  n={len(low_pe_returns):<3}  Avg={avg_low_pe:+6.2f}%  Median={median_low_pe:+6.2f}%  Std={std_low_pe:5.2f}%")
            print(f"  ⚡ DIFFERENCE:   Low P/E outperforms by {difference:+.2f}% on average")
            
            # Calculate percentage outperformance
            if avg_high_pe != 0:
                pct_outperform = (difference / abs(avg_high_pe)) * 100
                print(f"     ({pct_outperform:+.1f}% relative outperformance)")
    
    # Summary table
    print("\n" + "="*110)
    print("SUMMARY TABLE: Low P/E Outperformance (Average Return Difference)")
    print("="*110)
    print(f"{'EPS Type':<20} {'1Q Diff':<15} {'2Q Diff':<15} {'3Q Diff':<15} {'4Q Diff':<15} {'Avg Diff':<15}")
    print("-"*110)
    
    for eps_col in eps_columns:
        if eps_col not in summary_results:
            continue
        
        diffs = [summary_results[eps_col][f'{q}Q']['diff'] for q in [1,2,3,4] if f'{q}Q' in summary_results[eps_col]]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        
        diff_str = [f"{summary_results[eps_col][f'{q}Q']['diff']:+.2f}%" if f'{q}Q' in summary_results[eps_col] else "N/A" for q in [1,2,3,4]]
        
        print(f"{eps_labels[eps_col]:<20} {diff_str[0]:<15} {diff_str[1]:<15} {diff_str[2]:<15} {diff_str[3]:<15} {avg_diff:+.2f}%")
    
    print("\n" + "="*110)
    print("📌 Interpretation:")
    print("   Positive difference = Low P/E earns MORE on average")
    print("   Negative difference = Low P/E earns LESS on average")
    print("   This shows the ACTUAL dollar value of P/E prediction")
    print("="*110)


if __name__ == '__main__':
    main()

