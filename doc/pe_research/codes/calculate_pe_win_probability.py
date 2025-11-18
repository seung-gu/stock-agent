"""Calculate win probability by P/E zones for all time periods (1Q, 2Q, 3Q, 4Q)."""

import pandas as pd
import yfinance as yf
import numpy as np
from pathlib import Path
from datetime import datetime

# 1. Load quarterly EPS data
excel_path = Path.home() / 'Downloads' / 'sp-500-eps-est.xlsx'
df = pd.read_excel(excel_path, sheet_name='ESTIMATES&PEs', engine='openpyxl')

start_row = 127
end_row = 277

dates_raw = df.iloc[start_row:end_row+1, 0].values
col_m = df.iloc[start_row:end_row+1, 12].values

quarterly_data = []
for date_val, m_val in zip(dates_raw, col_m):
    if pd.notna(date_val) and pd.notna(m_val):
        try:
            date_str = str(date_val).split('(')[0].strip()
            date_parsed = pd.to_datetime(date_str)
            quarterly_data.append({'Date': date_parsed, 'M': float(m_val)})
        except:
            pass

quarterly_df = pd.DataFrame(quarterly_data).set_index('Date').sort_index()

# 2. Get daily S&P 500 prices
sp500 = yf.Ticker("^GSPC")
daily_prices = sp500.history(start=quarterly_df.index[0], end=datetime.now())
daily_prices.index = daily_prices.index.tz_localize(None)

# 3. Map daily prices to quarterly EPS
daily_df = pd.DataFrame(index=daily_prices.index)
daily_df['Price'] = daily_prices['Close']

eps_values = []
for date in daily_df.index:
    future_quarters = quarterly_df[quarterly_df.index >= date]
    if len(future_quarters) > 0:
        quarter_end = future_quarters.index[0]
        eps_val = quarterly_df.loc[quarter_end, 'M']
        eps_values.append(eps_val)
    else:
        eps_values.append(np.nan)

daily_df['EPS'] = eps_values
daily_df = daily_df.dropna()

# 4. Calculate P/E ratio
daily_df['PE'] = daily_df['Price'] / daily_df['EPS']

# 5. Calculate returns for all periods
trading_days = {
    '1Q': 63,
    '2Q': 126,
    '3Q': 189,
    '4Q': 252
}

for period, days in trading_days.items():
    daily_df[f'Return_{period}'] = (daily_df['Price'].shift(-days) / daily_df['Price'] - 1) * 100

# Drop NaN
daily_df = daily_df.dropna()

print(f"Total samples: {len(daily_df):,}")

# 6. Define zones
p10 = daily_df['PE'].quantile(0.10)
p25 = daily_df['PE'].quantile(0.25)
p50 = daily_df['PE'].quantile(0.50)
p75 = daily_df['PE'].quantile(0.75)

zones = [
    ("초공격 (< 10%)", f"< {p10:.1f}", daily_df['PE'] < p10),
    ("공격 (10-25%)", f"{p10:.1f}-{p25:.1f}", (daily_df['PE'] >= p10) & (daily_df['PE'] < p25)),
    ("신중 (25-50%)", f"{p25:.1f}-{p50:.1f}", (daily_df['PE'] >= p25) & (daily_df['PE'] < p50)),
    ("경계 (50-75%)", f"{p50:.1f}-{p75:.1f}", (daily_df['PE'] >= p50) & (daily_df['PE'] < p75)),
    ("위험 (≥ 75%)", f"≥ {p75:.1f}", daily_df['PE'] >= p75),
]

print("\n" + "="*100)
print("구간별 × 기간별 수익 확률 매트릭스")
print("="*100)

for zone_name, pe_range, mask in zones:
    zone_data = daily_df[mask]
    print(f"\n{zone_name} (P/E {pe_range}) - 샘플: {len(zone_data):,}")
    print("-" * 100)
    
    for period in ['1Q', '2Q', '3Q', '4Q']:
        returns = zone_data[f'Return_{period}']
        avg_ret = returns.mean()
        median_ret = returns.median()
        win_count = (returns > 0).sum()
        total = len(returns)
        win_prob = win_count / total * 100
        
        print(f"  {period} (3mo × {period[0]}): "
              f"평균 {avg_ret:+6.2f}% | 중앙 {median_ret:+6.2f}% | "
              f"승률 {win_prob:5.1f}% ({win_count:,}/{total:,})")

print("\n✅ 완료!")

