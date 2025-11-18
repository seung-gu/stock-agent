"""Calculate actual probabilities of mean reversion for different P/E definitions."""

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
    col_i = df.iloc[start_row:end_row+1, 8].values   # Column I (NTM)
    col_j = df.iloc[start_row:end_row+1, 9].values   # Column J (TTM - Trailing)
    col_k = df.iloc[start_row:end_row+1, 10].values  # Column K (NTM)
    col_l = df.iloc[start_row:end_row+1, 11].values  # Column L (NTM)
    col_m = df.iloc[start_row:end_row+1, 12].values  # Column M (NTM)
    
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
    
    # 5. Analyze each EPS column
    eps_columns = ['I', 'J', 'K', 'L', 'M']
    eps_labels = {
        'I': 'Forward I',
        'J': 'Trailing (TTM)',
        'K': 'Forward K',
        'L': 'Forward L',
        'M': 'Forward M'
    }
    
    print("\n" + "="*100)
    print("PROBABILITY ANALYSIS: P/E Predicts Future Returns")
    print("="*100)
    
    all_results = {}
    
    for eps_col in eps_columns:
        if eps_col not in quarterly_df.columns:
            continue
        
        valid_data = quarterly_df[quarterly_df[eps_col].notna()].copy()
        valid_data[f'PE_{eps_col}'] = valid_data['Price'] / valid_data[eps_col]
        
        mean_pe = valid_data[f'PE_{eps_col}'].mean()
        std_pe = valid_data[f'PE_{eps_col}'].std()
        valid_data[f'Zscore_{eps_col}'] = (valid_data[f'PE_{eps_col}'] - mean_pe) / std_pe
        
        all_results[eps_col] = {}
        
        print(f"\n{'='*100}")
        print(f"📊 {eps_labels[eps_col]} (Column {eps_col})")
        print(f"{'='*100}")
        
        for n_quarters in [1, 2, 3, 4]:
            return_col = f'Return_{n_quarters}Q'
            
            valid_mask = valid_data[f'Zscore_{eps_col}'].notna() & valid_data[return_col].notna()
            zscore = valid_data[f'Zscore_{eps_col}'][valid_mask]
            returns = valid_data[return_col][valid_mask]
            
            if len(zscore) < 10:
                continue
            
            # Use MEDIAN as threshold (not zero)
            median_return = returns.median()
            
            # Count quadrants
            high_pe_low_return = ((zscore > 0) & (returns < median_return)).sum()  # Correct prediction
            high_pe_high_return = ((zscore > 0) & (returns >= median_return)).sum()  # Wrong prediction
            low_pe_high_return = ((zscore < 0) & (returns >= median_return)).sum()   # Correct prediction
            low_pe_low_return = ((zscore < 0) & (returns < median_return)).sum()    # Wrong prediction
            
            total_high_pe = high_pe_low_return + high_pe_high_return
            total_low_pe = low_pe_high_return + low_pe_low_return
            
            # Calculate probabilities
            prob_low_return_when_high_pe = (high_pe_low_return / total_high_pe * 100) if total_high_pe > 0 else 0
            prob_high_return_when_low_pe = (low_pe_high_return / total_low_pe * 100) if total_low_pe > 0 else 0
            
            correct_predictions = high_pe_low_return + low_pe_high_return
            total_predictions = len(zscore)
            overall_accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            
            # Store results
            all_results[eps_col][f'{n_quarters}Q'] = {
                'prob_low_when_high': prob_low_return_when_high_pe,
                'prob_high_when_low': prob_high_return_when_low_pe,
                'accuracy': overall_accuracy,
                'n': total_predictions
            }
            
            # Calculate correlation for reference
            corr = zscore.corr(returns)
            
            print(f"\n{n_quarters}Q Forward ({n_quarters*3} months) - Correlation: {corr:+.3f}, Median Return: {median_return:.2f}%")
            print(f"  Total samples: {total_predictions}")
            print(f"  High P/E (Z>0) → Below Median Return: {high_pe_low_return}/{total_high_pe} = {prob_low_return_when_high_pe:.1f}%")
            print(f"  Low P/E (Z<0) → Above Median Return: {low_pe_high_return}/{total_low_pe} = {prob_high_return_when_low_pe:.1f}%")
            print(f"  Overall Accuracy: {correct_predictions}/{total_predictions} = {overall_accuracy:.1f}%")
    
    # Summary table
    print("\n" + "="*100)
    print("SUMMARY TABLE: Prediction Accuracy")
    print("="*100)
    print(f"{'EPS Type':<20} {'1Q Acc':<12} {'2Q Acc':<12} {'3Q Acc':<12} {'4Q Acc':<12} {'Avg Acc':<12}")
    print("-"*100)
    
    for eps_col in eps_columns:
        if eps_col not in all_results:
            continue
        
        accuracies = [all_results[eps_col][f'{q}Q']['accuracy'] for q in [1,2,3,4] if f'{q}Q' in all_results[eps_col]]
        avg_acc = sum(accuracies) / len(accuracies) if accuracies else 0
        
        acc_str = [f"{all_results[eps_col][f'{q}Q']['accuracy']:.1f}%" if f'{q}Q' in all_results[eps_col] else "N/A" for q in [1,2,3,4]]
        
        print(f"{eps_labels[eps_col]:<20} {acc_str[0]:<12} {acc_str[1]:<12} {acc_str[2]:<12} {acc_str[3]:<12} {avg_acc:.1f}%")
    
    print("\n" + "="*100)
    print("📌 Interpretation:")
    print("   Accuracy > 60%: Strong predictive power")
    print("   Accuracy 55-60%: Moderate predictive power")
    print("   Accuracy 50-55%: Weak predictive power")
    print("   Accuracy ~50%: No predictive power (coin flip)")
    print("="*100)


if __name__ == '__main__':
    main()

