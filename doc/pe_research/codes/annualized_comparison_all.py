"""Compare annualized return differentials across all P/E definitions (I, J, K, L, M)."""

import pandas as pd
import yfinance as yf
from pathlib import Path


def main():
    # 1. Get S&P 500 Price data
    print("Fetching S&P 500 Price data...")
    sp500 = yf.Ticker("^GSPC")
    price_df = sp500.history(period="max")
    price_df.index = price_df.index.tz_localize(None)
    
    # 2. Load quarterly EPS
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
    
    # 3. Get Price at each quarter-end
    quarterly_prices = []
    for q_date in quarterly_df.index:
        start_window = q_date - pd.Timedelta(days=7)
        end_window = q_date + pd.Timedelta(days=7)
        
        mask = (price_df.index >= start_window) & (price_df.index <= end_window)
        window_prices = price_df.loc[mask, 'Close']
        
        if len(window_prices) > 0:
            quarterly_prices.append(window_prices.mean())
        else:
            price_dates = price_df.index[price_df.index >= q_date]
            if len(price_dates) > 0:
                quarterly_prices.append(price_df.loc[price_dates[0], 'Close'])
            else:
                quarterly_prices.append(None)
    
    quarterly_df['Price'] = quarterly_prices
    quarterly_df = quarterly_df[quarterly_df['Price'].notna()].copy()
    
    # 4. Calculate future returns for all quarters
    for n_quarters in [1, 2, 3, 4]:
        quarterly_df[f'Return_{n_quarters}Q'] = quarterly_df['Price'].pct_change(n_quarters).shift(-n_quarters) * 100
    
    # 5. Analyze each EPS column
    eps_columns = {'I': 'Column I', 'J': 'Column J (Trailing)', 'K': 'Column K', 'L': 'Column L', 'M': 'Column M'}
    
    print("\n" + "="*110)
    print("연율화 초과수익 비교: 모든 P/E 정의 (I, J, K, L, M)")
    print("="*110)
    
    summary_results = {}
    
    for eps_col, label in eps_columns.items():
        if eps_col not in quarterly_df.columns:
            continue
        
        valid_data = quarterly_df[quarterly_df[eps_col].notna()].copy()
        valid_data[f'PE_{eps_col}'] = valid_data['Price'] / valid_data[eps_col]
        
        mean_pe = valid_data[f'PE_{eps_col}'].mean()
        std_pe = valid_data[f'PE_{eps_col}'].std()
        valid_data[f'Zscore_{eps_col}'] = (valid_data[f'PE_{eps_col}'] - mean_pe) / std_pe
        
        print(f"\n{'='*110}")
        print(f"{label}")
        print(f"{'='*110}")
        
        annualized_diffs = []
        
        for n_quarters in [1, 2, 3, 4]:
            return_col = f'Return_{n_quarters}Q'
            
            valid_mask = valid_data[f'Zscore_{eps_col}'].notna() & valid_data[return_col].notna()
            zscore = valid_data[f'Zscore_{eps_col}'][valid_mask]
            returns = valid_data[return_col][valid_mask]
            
            if len(zscore) < 10:
                continue
            
            # Calculate average returns by group
            high_pe_returns = returns[zscore > 0]
            low_pe_returns = returns[zscore < 0]
            
            avg_high_pe = high_pe_returns.mean()
            avg_low_pe = low_pe_returns.mean()
            difference = avg_low_pe - avg_high_pe
            
            # Annualize: (1 + quarterly_return)^(4/n_quarters) - 1
            # Simplified: quarterly_return * (4 / n_quarters)
            annualized_diff = difference * (4 / n_quarters)
            
            annualized_diffs.append(annualized_diff)
            
            print(f"{n_quarters}Q: Low={avg_low_pe:+6.2f}%, High={avg_high_pe:+6.2f}%, Diff={difference:+6.2f}%, Annualized Diff={annualized_diff:+6.2f}%/yr")
        
        avg_annualized = sum(annualized_diffs) / len(annualized_diffs) if annualized_diffs else 0
        summary_results[eps_col] = {'label': label, 'avg_annualized': avg_annualized, 'diffs': annualized_diffs}
        
        print(f"평균 연율화 초과수익: {avg_annualized:+.2f}% / 년")
    
    # Summary table
    print("\n" + "="*110)
    print("요약표: 연율화 초과수익 비교")
    print("="*110)
    print(f"{'EPS 정의':<25} {'1Q→연율화':<15} {'2Q→연율화':<15} {'3Q→연율화':<15} {'4Q→연율화':<15} {'평균':<12}")
    print("-"*110)
    
    for eps_col in ['I', 'J', 'K', 'L', 'M']:
        if eps_col not in summary_results:
            continue
        
        result = summary_results[eps_col]
        label = result['label']
        diffs = result['diffs']
        avg = result['avg_annualized']
        
        if len(diffs) >= 4:
            print(f"{label:<25} {diffs[0]:>+6.2f}%/yr    {diffs[1]:>+6.2f}%/yr    {diffs[2]:>+6.2f}%/yr    {diffs[3]:>+6.2f}%/yr    {avg:>+6.2f}%")
    
    print("\n" + "="*110)
    print("📌 핵심:")
    print("   - 연율화 초과수익이 일정하면 = 모든 기간에서 일관된 효과")
    print("   - 평균이 클수록 = 해당 P/E 정의의 예측력 높음")
    print("="*110)


if __name__ == '__main__':
    main()

