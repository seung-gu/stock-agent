"""Test mean reversion with Trailing P/E (Column J - TTM)."""

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
    
    # 2. Load quarterly Trailing EPS (J)
    print("Loading quarterly Trailing EPS (Column J - TTM)...")
    excel_path = Path.home() / 'Downloads' / 'sp-500-eps-est.xlsx'
    df = pd.read_excel(excel_path, sheet_name='ESTIMATES&PEs', engine='openpyxl')
    
    start_row = 127
    end_row = 277
    
    dates_raw = df.iloc[start_row:end_row+1, 0].values
    col_j = df.iloc[start_row:end_row+1, 9].values  # Column J (Trailing TTM)
    
    data_list = []
    for date_val, j_val in zip(dates_raw, col_j):
        if pd.notna(date_val) and pd.notna(j_val):
            try:
                date_str = str(date_val).split('(')[0].strip()
                date_parsed = pd.to_datetime(date_str)
                data_list.append({'Date': date_parsed, 'J': float(j_val)})
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
    
    # 5. Calculate Trailing P/E
    quarterly_df['Trailing_PE'] = quarterly_df['Price'] / quarterly_df['J']
    
    # Calculate Z-score
    mean_pe = quarterly_df['Trailing_PE'].mean()
    std_pe = quarterly_df['Trailing_PE'].std()
    quarterly_df['PE_Zscore'] = (quarterly_df['Trailing_PE'] - mean_pe) / std_pe
    
    print("\n" + "="*80)
    print("TRAILING P/E STATISTICS (Column J - TTM)")
    print("="*80)
    print(f"Data points: {len(quarterly_df)} quarters")
    print(f"Mean P/E: {mean_pe:.2f}")
    print(f"Std P/E: {std_pe:.2f}")
    print(f"Current P/E: {quarterly_df['Trailing_PE'].iloc[-1]:.2f}")
    print(f"Current Z-score: {quarterly_df['PE_Zscore'].iloc[-1]:.2f}")
    
    # 6. Calculate correlations
    print("\n" + "="*80)
    print("MEAN REVERSION TEST: Trailing P/E Z-score vs Future Returns")
    print("(Negative correlation = mean reversion exists)")
    print("="*80)
    
    correlations = {}
    for n_quarters in [1, 2, 3, 4]:
        return_col = f'Return_{n_quarters}Q'
        
        valid_mask = quarterly_df['PE_Zscore'].notna() & quarterly_df[return_col].notna()
        zscore_clean = quarterly_df['PE_Zscore'][valid_mask]
        return_clean = quarterly_df[return_col][valid_mask]
        
        if len(zscore_clean) > 1:
            corr = zscore_clean.corr(return_clean)
            correlations[n_quarters] = corr
            
            if corr < -0.3:
                interpretation = "🟢 STRONG mean reversion"
            elif corr < -0.1:
                interpretation = "🟡 MODERATE mean reversion"
            elif corr < 0:
                interpretation = "⚪ WEAK mean reversion"
            else:
                interpretation = "🔴 NO mean reversion"
            
            print(f"{n_quarters}Q ahead ({n_quarters*3} months): r={corr:+.4f} ({len(zscore_clean)} quarters) - {interpretation}")
    
    avg_corr = sum(correlations.values()) / len(correlations)
    print(f"\nAverage correlation: {avg_corr:+.4f}")
    
    # 7. Visualize
    print(f"\nGenerating chart for Trailing P/E (Column J)...")
    
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)
    fig.suptitle(f'Trailing P/E Mean Reversion Analysis (TTM - Column J) - Avg r={avg_corr:.3f}', 
                 fontsize=16, fontweight='bold')
    
    # Chart 1 (Top, span 2 columns): P/E over time
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(quarterly_df.index, quarterly_df['Trailing_PE'], linewidth=2, color='#1f77b4', 
             marker='o', markersize=4, label='Trailing P/E (TTM)')
    ax1.axhline(y=mean_pe, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_pe:.2f}')
    ax1.axhline(y=mean_pe + std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, 
                label=f'+1σ: {mean_pe + std_pe:.2f}')
    ax1.axhline(y=mean_pe - std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.7,
                label=f'-1σ: {mean_pe - std_pe:.2f}')
    ax1.fill_between(quarterly_df.index, mean_pe - std_pe, mean_pe + std_pe, alpha=0.1, color='orange')
    ax1.set_ylabel('Trailing P/E Ratio', fontsize=11)
    ax1.set_title('Trailing P/E over Time (Column J - TTM) - 30 Years', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # Charts 2-5: Scatter plots for 1Q, 2Q, 3Q, 4Q
    scatter_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    quarters = [1, 2, 3, 4]
    
    for idx, n_quarters in enumerate(quarters):
        row = 1 + idx // 2
        col_idx = idx % 2
        ax = fig.add_subplot(gs[row, col_idx])
        
        return_col = f'Return_{n_quarters}Q'
        valid_mask = quarterly_df['PE_Zscore'].notna() & quarterly_df[return_col].notna()
        zscore_data = quarterly_df['PE_Zscore'][valid_mask]
        return_data = quarterly_df[return_col][valid_mask]
        
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
    
    chart_path = '/Users/seung-gu/PycharmProjects/stock-agent/charts/pe_mean_reversion_J_trailing.png'
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    print(f"✅ Chart saved: {chart_path}")


if __name__ == '__main__':
    main()

