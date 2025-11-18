"""Compare quartile analysis for all P/E definitions (I, K, L, M)."""

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
    col_k = df.iloc[start_row:end_row+1, 10].values
    col_l = df.iloc[start_row:end_row+1, 11].values
    col_m = df.iloc[start_row:end_row+1, 12].values
    
    data_list = []
    for date_val, i_val, k_val, l_val, m_val in zip(dates_raw, col_i, col_k, col_l, col_m):
        if pd.notna(date_val):
            try:
                date_str = str(date_val).split('(')[0].strip()
                date_parsed = pd.to_datetime(date_str)
                row_data = {'Date': date_parsed}
                if pd.notna(i_val):
                    row_data['I'] = float(i_val)
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
    
    # Filter to last 10 years
    cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=10)
    quarterly_10y = quarterly_df[quarterly_df.index >= cutoff_date].copy()
    
    # 4. Calculate future returns
    quarterly_10y['Return_4Q'] = quarterly_10y['Price'].pct_change(4).shift(-4) * 100
    
    # 5. Analyze each P/E type
    eps_columns = {'I': 'Column I (현재+지난3Q 예측)', 
                   'K': 'Column K (현재실측+다음3Q)', 
                   'L': 'Column L (현재예측+다음3Q)', 
                   'M': 'Column M (다음4Q 예측)'}
    
    print("\n" + "="*100)
    print("10년 데이터 기준 P/E 구간별 수익률 비교 (I, K, L, M)")
    print("="*100)
    
    all_results = {}
    
    for eps_col, label in eps_columns.items():
        if eps_col not in quarterly_10y.columns:
            continue
        
        valid_data = quarterly_10y[quarterly_10y[eps_col].notna()].copy()
        valid_data[f'PE_{eps_col}'] = valid_data['Price'] / valid_data[eps_col]
        
        # Remove outliers
        valid_data = valid_data[(valid_data[f'PE_{eps_col}'] > 0) & (valid_data[f'PE_{eps_col}'] < 100)].copy()
        
        pe_values = valid_data[f'PE_{eps_col}']
        
        # Calculate quartiles
        q25 = pe_values.quantile(0.25)
        q50 = pe_values.quantile(0.50)
        q75 = pe_values.quantile(0.75)
        
        mean_pe = pe_values.mean()
        current_pe = pe_values.iloc[-1]
        
        # Calculate average returns by quartile
        valid_returns = valid_data[valid_data['Return_4Q'].notna()].copy()
        
        quartile_results = []
        
        # Bottom 25%
        mask_q1 = valid_returns[f'PE_{eps_col}'] < q25
        if mask_q1.sum() > 0:
            avg_return = valid_returns.loc[mask_q1, 'Return_4Q'].mean()
            quartile_results.append(('0-25%', f'< {q25:.1f}', mask_q1.sum(), avg_return))
        
        # 25-50%
        mask_q2 = (valid_returns[f'PE_{eps_col}'] >= q25) & (valid_returns[f'PE_{eps_col}'] < q50)
        if mask_q2.sum() > 0:
            avg_return = valid_returns.loc[mask_q2, 'Return_4Q'].mean()
            quartile_results.append(('25-50%', f'{q25:.1f}-{q50:.1f}', mask_q2.sum(), avg_return))
        
        # 50-75%
        mask_q3 = (valid_returns[f'PE_{eps_col}'] >= q50) & (valid_returns[f'PE_{eps_col}'] < q75)
        if mask_q3.sum() > 0:
            avg_return = valid_returns.loc[mask_q3, 'Return_4Q'].mean()
            quartile_results.append(('50-75%', f'{q50:.1f}-{q75:.1f}', mask_q3.sum(), avg_return))
        
        # Top 25%
        mask_q4 = valid_returns[f'PE_{eps_col}'] >= q75
        if mask_q4.sum() > 0:
            avg_return = valid_returns.loc[mask_q4, 'Return_4Q'].mean()
            quartile_results.append(('75-100%', f'≥ {q75:.1f}', mask_q4.sum(), avg_return))
        
        all_results[eps_col] = {
            'label': label,
            'mean': mean_pe,
            'q25': q25,
            'q50': q50,
            'q75': q75,
            'current': current_pe,
            'quartiles': quartile_results
        }
        
        print(f"\n{'='*100}")
        print(f"{label}")
        print(f"{'='*100}")
        print(f"평균 P/E: {mean_pe:.2f} | 현재 P/E: {current_pe:.2f}")
        print(f"25%: {q25:.1f} | 50%: {q50:.1f} | 75%: {q75:.1f}")
        print(f"\n구간별 평균 1년 수익률:")
        for percentile, pe_range, n, avg_return in quartile_results:
            print(f"  {percentile:>10} (P/E {pe_range:>12}): {avg_return:>+6.2f}% (n={n})")
    
    # Summary comparison table
    print("\n" + "="*100)
    print("비교 요약표: 구간별 평균 수익률")
    print("="*100)
    print(f"{'EPS 정의':<30} {'하위25%':<12} {'25-50%':<12} {'50-75%':<12} {'상위25%':<12} {'스프레드':<12}")
    print("-"*100)
    
    for eps_col in ['I', 'K', 'L', 'M']:
        if eps_col not in all_results:
            continue
        
        results = all_results[eps_col]
        label = results['label']
        quartiles = results['quartiles']
        
        # Extract returns for each quartile
        returns_dict = {q[0]: q[3] for q in quartiles}
        
        q1_ret = returns_dict.get('0-25%', 0)
        q2_ret = returns_dict.get('25-50%', 0)
        q3_ret = returns_dict.get('50-75%', 0)
        q4_ret = returns_dict.get('75-100%', 0)
        
        spread = q1_ret - q4_ret
        
        print(f"{label:<30} {q1_ret:>+6.2f}%    {q2_ret:>+6.2f}%    {q3_ret:>+6.2f}%    {q4_ret:>+6.2f}%    {spread:>+6.2f}%p")
    
    print("\n" + "="*100)
    print("📌 핵심 발견:")
    print("   - 스프레드 = 하위25% - 상위25% 수익률 차이")
    print("   - 스프레드가 클수록 해당 P/E 정의의 차별력이 높음")
    print("="*100)


if __name__ == '__main__':
    main()

