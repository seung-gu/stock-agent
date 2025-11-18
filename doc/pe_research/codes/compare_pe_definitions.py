"""Compare mean reversion across different Forward P/E definitions (I, K, L, M)."""

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def main():
    # 1. Get S&P 500 Price data (30 years)
    print("Fetching S&P 500 Price data (30 years)...")
    sp500 = yf.Ticker("^GSPC")
    price_df = sp500.history(period="max")
    price_df.index = price_df.index.tz_localize(None)
    
    # 2. Load quarterly EPS (I, K, L, M)
    print("Loading quarterly Forward EPS (I, K, L, M)...")
    excel_path = Path.home() / 'Downloads' / 'sp-500-eps-est.xlsx'
    df = pd.read_excel(excel_path, sheet_name='ESTIMATES&PEs', engine='openpyxl')
    
    start_row = 127
    end_row = 277
    
    dates_raw = df.iloc[start_row:end_row+1, 0].values
    col_i = df.iloc[start_row:end_row+1, 8].values   # Column I
    col_k = df.iloc[start_row:end_row+1, 10].values  # Column K
    col_l = df.iloc[start_row:end_row+1, 11].values  # Column L
    col_m = df.iloc[start_row:end_row+1, 12].values  # Column M
    
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
    
    print(f"All quarterly data: {len(quarterly_df)} quarters")
    print(f"Date range: {quarterly_df.index[0].date()} to {quarterly_df.index[-1].date()}")
    
    # 3. Get Price at each quarter-end (using 2-week average around quarter-end)
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
    
    # 4. Calculate future returns (1Q, 2Q, 3Q, 4Q ahead)
    for n_quarters in [1, 2, 3, 4]:
        quarterly_df[f'Return_{n_quarters}Q'] = quarterly_df['Price'].pct_change(n_quarters).shift(-n_quarters) * 100
    
    # 5. Calculate Forward P/E for each EPS column (I, K, L, M)
    eps_columns = ['I', 'K', 'L', 'M']
    results = {}
    
    print("\n" + "="*90)
    print("FORWARD P/E STATISTICS BY EPS DEFINITION")
    print("="*90)
    
    for eps_col in eps_columns:
        if eps_col not in quarterly_df.columns:
            continue
        
        # Filter out rows where EPS is NaN
        valid_data = quarterly_df[quarterly_df[eps_col].notna()].copy()
        
        # Calculate P/E
        valid_data[f'PE_{eps_col}'] = valid_data['Price'] / valid_data[eps_col]
        
        # Calculate Z-score
        mean_pe = valid_data[f'PE_{eps_col}'].mean()
        std_pe = valid_data[f'PE_{eps_col}'].std()
        valid_data[f'Zscore_{eps_col}'] = (valid_data[f'PE_{eps_col}'] - mean_pe) / std_pe
        
        # Calculate correlations for each quarter
        correlations = {}
        for n_quarters in [1, 2, 3, 4]:
            return_col = f'Return_{n_quarters}Q'
            valid_mask = valid_data[f'Zscore_{eps_col}'].notna() & valid_data[return_col].notna()
            zscore_clean = valid_data[f'Zscore_{eps_col}'][valid_mask]
            return_clean = valid_data[return_col][valid_mask]
            
            if len(zscore_clean) > 1:
                corr = zscore_clean.corr(return_clean)
                correlations[f'{n_quarters}Q'] = corr
        
        # Store results
        results[eps_col] = {
            'data': valid_data,
            'mean': mean_pe,
            'std': std_pe,
            'current_pe': valid_data[f'PE_{eps_col}'].iloc[-1],
            'current_zscore': valid_data[f'Zscore_{eps_col}'].iloc[-1],
            'correlations': correlations,
            'n_quarters': len(valid_data)
        }
        
        print(f"\n📊 Column {eps_col} (NTM EPS):")
        print(f"  Data points: {len(valid_data)} quarters")
        print(f"  Mean P/E: {mean_pe:.2f}")
        print(f"  Std P/E: {std_pe:.2f}")
        print(f"  Current P/E: {valid_data[f'PE_{eps_col}'].iloc[-1]:.2f}")
        print(f"  Current Z-score: {valid_data[f'Zscore_{eps_col}'].iloc[-1]:.2f}")
    
    # 6. Print comparison table
    print("\n" + "="*90)
    print("MEAN REVERSION COMPARISON TABLE (P/E Z-score vs Future Returns)")
    print("="*90)
    print(f"{'EPS Col':<10} {'1Q (3mo)':<15} {'2Q (6mo)':<15} {'3Q (9mo)':<15} {'4Q (12mo)':<15} {'Avg':<10}")
    print("-"*90)
    
    for eps_col in eps_columns:
        if eps_col not in results:
            continue
        
        corrs = results[eps_col]['correlations']
        corr_values = [corrs.get(f'{q}Q', 0) for q in [1, 2, 3, 4]]
        avg_corr = sum(corr_values) / len(corr_values) if corr_values else 0
        
        print(f"{eps_col:<10} {corr_values[0]:>+.4f}        {corr_values[1]:>+.4f}        "
              f"{corr_values[2]:>+.4f}        {corr_values[3]:>+.4f}        {avg_corr:>+.4f}")
    
    print("\n" + "="*90)
    print("📌 Interpretation: Negative correlation = Mean reversion (high P/E → lower returns)")
    print("   Strong: < -0.3  |  Moderate: -0.3 to -0.1  |  Weak: -0.1 to 0  |  None: > 0")
    print("="*90)
    
    # 7. Find best EPS column (strongest average mean reversion)
    avg_corrs = {}
    for eps_col in eps_columns:
        if eps_col in results:
            corrs = results[eps_col]['correlations']
            avg_corrs[eps_col] = sum(corrs.values()) / len(corrs) if corrs else 0
    
    best_eps_col = min(avg_corrs, key=avg_corrs.get)
    print(f"\n🏆 Best EPS Definition: Column {best_eps_col} (Avg Correlation: {avg_corrs[best_eps_col]:+.4f})")
    
    # 8. Visualize EACH EPS column separately (I, K, L, M)
    print(f"\nGenerating individual charts for each EPS column (I, K, L, M)...")
    
    scatter_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    quarters = [1, 2, 3, 4]
    
    for eps_col in eps_columns:
        if eps_col not in results:
            continue
        
        data = results[eps_col]['data']
        mean_pe = results[eps_col]['mean']
        std_pe = results[eps_col]['std']
        avg_corr = avg_corrs.get(eps_col, 0)
        
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
        fig.suptitle(f'Forward P/E Mean Reversion Analysis - Column {eps_col} (Avg r={avg_corr:.3f})', 
                     fontsize=16, fontweight='bold')
        
        # Chart 1 (Top, span 2 columns): P/E over time
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(data.index, data[f'PE_{eps_col}'], linewidth=2, color='#1f77b4', 
                 marker='o', markersize=4, label=f'Forward P/E ({eps_col})')
        ax1.axhline(y=mean_pe, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_pe:.2f}')
        ax1.axhline(y=mean_pe + std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, 
                    label=f'+1σ: {mean_pe + std_pe:.2f}')
        ax1.axhline(y=mean_pe - std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.7,
                    label=f'-1σ: {mean_pe - std_pe:.2f}')
        ax1.fill_between(data.index, mean_pe - std_pe, mean_pe + std_pe, alpha=0.1, color='orange')
        ax1.set_ylabel('Forward P/E Ratio', fontsize=11)
        ax1.set_title(f'Forward P/E over Time (Column {eps_col}) - 30 Years', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=10, loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Charts 2-5: Scatter plots for 1Q, 2Q, 3Q, 4Q
        for idx, n_quarters in enumerate(quarters):
            row = 1 + idx // 2
            col_idx = idx % 2
            ax = fig.add_subplot(gs[row, col_idx])
            
            return_col = f'Return_{n_quarters}Q'
            valid_mask = data[f'Zscore_{eps_col}'].notna() & data[return_col].notna()
            zscore_data = data[f'Zscore_{eps_col}'][valid_mask]
            return_data = data[return_col][valid_mask]
            
            corr = zscore_data.corr(return_data)
            
            ax.scatter(zscore_data, return_data, s=60, alpha=0.6, color=scatter_colors[idx], 
                       edgecolors='black', linewidths=0.8)
            
            # Add trend line
            if len(zscore_data) > 1:
                z = np.polyfit(zscore_data, return_data, 1)
                p = np.poly1d(z)
                x_line = np.linspace(zscore_data.min(), zscore_data.max(), 100)
                ax.plot(x_line, p(x_line), "r--", linewidth=2, alpha=0.7, label=f'r={corr:.3f}')
            
            ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
            ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
            ax.set_xlabel('P/E Z-score', fontsize=10)
            ax.set_ylabel(f'{n_quarters}Q Ahead Return (%)', fontsize=10)
            ax.set_title(f'{n_quarters}Q Forward Returns ({n_quarters*3} months)', fontsize=11, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        chart_path = f'/Users/seung-gu/PycharmProjects/stock-agent/charts/pe_mean_reversion_{eps_col}.png'
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        print(f"✅ Chart saved: {chart_path}")
        plt.close()


if __name__ == '__main__':
    main()

