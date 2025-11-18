"""
Figure 1: Operating vs As Reported Earnings (1988-2025)
37년간 Forward 4Q EPS 비교 차트 생성
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# 데이터 로드
df = pd.read_excel('sp-500-eps-est.xlsx', sheet_name='ESTIMATES&PEs', skiprows=5)

# 날짜 파싱
df['Date'] = pd.to_datetime(df.iloc[:, 0].astype(str).str.split('(').str[0].str.strip())

# Operating (M)과 As Reported (N) EPS
df['Operating'] = pd.to_numeric(df.iloc[:, 12], errors='coerce')  # Column M
df['As_Reported'] = pd.to_numeric(df.iloc[:, 13], errors='coerce')  # Column N
df['Diff'] = df['Operating'] - df['As_Reported']

# NaN 제거
df = df.dropna(subset=['Date', 'Operating', 'As_Reported'])

# Figure 생성
fig, axes = plt.subplots(4, 1, figsize=(14, 16))

# Panel 1: Forward 4Q EPS 비교
ax1 = axes[0]
ax1.plot(df['Date'], df['Operating'], label='Operating (M)', linewidth=2, color='blue')
ax1.plot(df['Date'], df['As_Reported'], label='As Reported (N)', linewidth=2, color='red')
ax1.set_title('Forward 4Q EPS: Operating vs As Reported (1988-2025)', fontsize=14, fontweight='bold')
ax1.set_ylabel('EPS ($)', fontsize=12)
ax1.legend()
ax1.grid(alpha=0.3)

# 위기 기간 음영
ax1.axvspan(datetime(2000, 1, 1), datetime(2002, 12, 31), alpha=0.2, color='red', label='Dot-com')
ax1.axvspan(datetime(2008, 1, 1), datetime(2009, 12, 31), alpha=0.2, color='orange', label='Financial Crisis')
ax1.axvspan(datetime(2020, 2, 1), datetime(2020, 6, 30), alpha=0.2, color='purple', label='COVID-19')

# Panel 2-4: 추가 비교 차트들...
# (필요 시 확장)

plt.tight_layout()
plt.savefig('output/pe_operating_vs_reported_full_en.png', dpi=300, bbox_inches='tight')
print("✅ Figure 1 생성 완료!")

