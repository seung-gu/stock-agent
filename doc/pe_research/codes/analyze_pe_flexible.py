"""
유연한 분기 범위로 S&P 500 Forward P/E 분석

사용 예시:
- Q[0:4] → Q(0), Q(1), Q(2), Q(3)
- Q[1:5] → Q(1), Q(2), Q(3), Q(4)
- Q[-3:1] → Q(-3), Q(-2), Q(-1), Q(0)
- Q[-1:3] → Q(-1), Q(0), Q(1), Q(2)
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import stats
from pathlib import Path
import warnings
import sys
warnings.filterwarnings('ignore')

# 설정
OUTPUT_DIR = Path('doc/pe_research')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 데이터 로드 함수
def load_price_data():
    """S&P 500 가격 데이터 로드"""
    print("Loading S&P 500 price data from yfinance...")
    ticker = yf.Ticker("^GSPC")
    df = ticker.history(period="max")
    df.index = df.index.tz_localize(None)  # timezone 제거
    return df

def get_quarter_range(trade_date, quarter_start, quarter_end):
    """
    거래일 기준으로 분기 범위 계산
    
    Args:
        trade_date: 거래일
        quarter_start: 시작 분기 인덱스 (예: 0, 1, -3)
        quarter_end: 끝 분기 인덱스 (예: 4, 5, 1)
    
    Returns:
        list of (q_num, q_year) tuples
    """
    trade_year = trade_date.year
    trade_month = trade_date.month
    
    # 거래일 기준으로 가장 최근에 끝난 분기 결정 (Q(0))
    if trade_month <= 3:
        q0_num = 4
        q0_year = trade_year - 1
    elif trade_month <= 6:
        q0_num = 1
        q0_year = trade_year
    elif trade_month <= 9:
        q0_num = 2
        q0_year = trade_year
    else:
        q0_num = 3
        q0_year = trade_year
    
    # 특별 케이스: Q[1:5]는 기존 방식과 동일하게 "다음 분기부터 시작하는 4분기"
    # 기존 analyze_pe_q1_to_q4.py의 로직과 동일하게 처리
    if quarter_start == 1 and quarter_end == 5:
        # 거래일 기준으로 다음 분기부터 시작하는 4분기 결정
        if trade_month <= 3:
            # 1-3월: 다음 분기는 Q2, Q3, Q4, Q1(다음년도)
            return [(2, trade_year), (3, trade_year), (4, trade_year), (1, trade_year + 1)]
        elif trade_month <= 6:
            # 4-6월: 다음 분기는 Q3, Q4, Q1(다음년도), Q2(다음년도)
            return [(3, trade_year), (4, trade_year), (1, trade_year + 1), (2, trade_year + 1)]
        elif trade_month <= 9:
            # 7-9월: 다음 분기는 Q4, Q1(다음년도), Q2(다음년도), Q3(다음년도)
            return [(4, trade_year), (1, trade_year + 1), (2, trade_year + 1), (3, trade_year + 1)]
        else:
            # 10-12월: 다음 분기는 Q1(다음년도), Q2(다음년도), Q3(다음년도), Q4(다음년도)
            return [(1, trade_year + 1), (2, trade_year + 1), (3, trade_year + 1), (4, trade_year + 1)]
    
    # 일반적인 경우: Q(0) 기준으로 offset 계산
    quarters = []
    for q_offset in range(quarter_start, quarter_end):
        q_num = q0_num + q_offset
        q_year = q0_year
        
        # 분기 넘어가면 조정
        while q_num <= 0:
            q_num += 4
            q_year -= 1
        while q_num > 4:
            q_num -= 4
            q_year += 1
        
        quarters.append((q_num, q_year))
    
    return quarters

def calculate_percentile_returns(pe_series, returns_series, percentiles=[25, 50, 75]):
    """백분위별 수익률 계산"""
    valid_mask = ~(pe_series.isna() | returns_series.isna())
    pe_valid = pe_series[valid_mask]
    returns_valid = returns_series[valid_mask]
    
    if len(pe_valid) == 0:
        return {}
    
    pe_percentiles = np.percentile(pe_valid, percentiles)
    
    results = {}
    
    mask_bottom = pe_valid <= pe_percentiles[0]
    results['Bottom 25%'] = {
        'pe_range': (pe_valid.min(), pe_percentiles[0]),
        'avg_return': returns_valid[mask_bottom].mean() if mask_bottom.sum() > 0 else np.nan,
        'count': mask_bottom.sum()
    }
    
    for i in range(len(percentiles) - 1):
        mask = (pe_valid > pe_percentiles[i]) & (pe_valid <= pe_percentiles[i+1])
        label = f"{percentiles[i]}-{percentiles[i+1]}%"
        results[label] = {
            'pe_range': (pe_percentiles[i], pe_percentiles[i+1]),
            'avg_return': returns_valid[mask].mean() if mask.sum() > 0 else np.nan,
            'count': mask.sum()
        }
    
    mask_top = pe_valid > pe_percentiles[-1]
    results['Top 25%'] = {
        'pe_range': (pe_percentiles[-1], pe_valid.max()),
        'avg_return': returns_valid[mask_top].mean() if mask_top.sum() > 0 else np.nan,
        'count': mask_top.sum()
    }
    
    return results

def create_pe_chart(pe_series, title):
    """P/E 시계열 그래프 생성"""
    fig, ax = plt.subplots(figsize=(16, 9))
    
    ax.plot(pe_series.index, pe_series.values, linewidth=2.5, color='#1f77b4', label='P/E Ratio', zorder=3)
    
    mean_pe = pe_series.mean()
    ax.axhline(y=mean_pe, color='gray', linestyle='--', linewidth=2, label=f'Mean: {mean_pe:.2f}', alpha=0.8, zorder=2)
    
    std_pe = pe_series.std()
    ax.axhline(y=mean_pe + std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.6, label=f'+1σ: {mean_pe + std_pe:.2f}', zorder=1)
    ax.axhline(y=mean_pe - std_pe, color='orange', linestyle=':', linewidth=1.5, alpha=0.6, label=f'-1σ: {mean_pe - std_pe:.2f}', zorder=1)
    
    ax.axhline(y=21, color='red', linestyle='--', linewidth=2, alpha=0.8, label='Critical Threshold: 21', zorder=2)
    
    latest_pe = pe_series.iloc[-1]
    latest_date = pe_series.index[-1]
    ax.plot(latest_date, latest_pe, 'ro', markersize=10, zorder=4, label=f'Current: {latest_pe:.2f}')
    
    ax.set_xlabel('Date', fontsize=13, fontweight='bold')
    ax.set_ylabel('P/E Ratio', fontsize=13, fontweight='bold')
    ax.set_title(title, fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    y_min = max(0, pe_series.min() * 0.8)
    y_max = pe_series.max() * 1.1
    ax.set_ylim(y_min, y_max)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_minor_locator(mdates.YearLocator())
    plt.xticks(rotation=45, ha='right')
    
    stats_text = f'n={len(pe_series):,} | Mean={mean_pe:.2f} | Std={std_pe:.2f} | Min={pe_series.min():.2f} | Max={pe_series.max():.2f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig

def main(quarter_start=1, quarter_end=5):
    """
    메인 분석 함수
    
    Args:
        quarter_start: 시작 분기 인덱스 (예: 0, 1, -3)
        quarter_end: 끝 분기 인덱스 (예: 4, 5, 1)
    """
    # 분기 범위 문자열 생성
    quarter_range_str = f"Q[{quarter_start}:{quarter_end}]"
    quarter_labels = []
    for i in range(quarter_start, quarter_end):
        if i < 0:
            quarter_labels.append(f"Q({i})")
        elif i == 0:
            quarter_labels.append("Q(0)")
        else:
            quarter_labels.append(f"Q({i})")
    quarter_label_str = "+".join(quarter_labels)
    
    print("=" * 80)
    print(f"{quarter_range_str} 방식 S&P 500 Forward P/E 분석")
    print(f"EPS 구성: {quarter_label_str}")
    print("=" * 80)
    
    # 1. 데이터 로드
    price_df = load_price_data()
    print(f"✓ Loaded {len(price_df)} price records")
    
    # EPS 데이터 로드
    eps_file = OUTPUT_DIR / "extracted_estimates.csv"
    
    if not eps_file.exists():
        print(f"\n❌ EPS 데이터 파일을 찾을 수 없습니다: {eps_file}")
        return
    
    extracted = pd.read_csv(eps_file)
    extracted['Date'] = pd.to_datetime(extracted['Report_Date'])
    
    print(f"Loading EPS data from {eps_file}...")
    quarter_cols = [col for col in extracted.columns if col.startswith('Q') and "'" in col]
    print(f"✓ Found {len(quarter_cols)} quarter columns")
    
    # 2. 일일 데이터로 P/E 계산
    print("\n" + "=" * 80)
    print("일일 데이터 P/E 계산 시작 (거래일 기준)")
    print("=" * 80)
    
    results = []
    
    # 모든 거래일에 대해 처리
    for trade_date in price_df.index:
        price = price_df.loc[trade_date, 'Close']
        
        if pd.isna(price) or price <= 0:
            continue
        
        # 거래일 기준으로 가장 최근 리포트 찾기
        valid_reports = extracted[extracted['Date'] <= trade_date]
        if len(valid_reports) == 0:
            continue
        
        report_row = valid_reports.iloc[-1]
        report_date = report_row['Date']
        
        # 분기 범위 계산
        quarters = get_quarter_range(trade_date, quarter_start, quarter_end)
        
        # 컬럼명 생성 및 값 추출
        def get_col_name(q_num, year):
            year_short = year % 100
            return f"Q{q_num}'{year_short:02d}"
        
        def extract_value(col_name):
            if col_name not in extracted.columns:
                return None
            value_str = str(report_row[col_name])
            if pd.isna(value_str) or value_str == '' or value_str == 'nan':
                return None
            value_str = value_str.replace('*', '').strip()
            try:
                return float(value_str)
            except:
                return None
        
        # 각 분기 값 추출
        quarter_values = []
        for q_num, q_year in quarters:
            col_name = get_col_name(q_num, q_year)
            value = extract_value(col_name)
            if value is None:
                break
            quarter_values.append(value)
        
        # 모든 분기 값이 있어야 함
        if len(quarter_values) != len(quarters):
            continue
        
        # EPS 계산
        eps = sum(quarter_values)
        
        if eps <= 0:
            continue
        
        pe = price / eps
        
        # 미래 수익률 계산
        def get_future_return(weeks):
            future_date = trade_date + pd.Timedelta(weeks=weeks)
            if future_date in price_df.index:
                future_price = price_df.loc[future_date, 'Close']
                return (future_price - price) / price * 100
            else:
                future_prices = price_df[price_df.index > trade_date]
                if len(future_prices) > 0:
                    target_days = weeks * 7
                    days_diff = (future_prices.index - trade_date).days
                    days_diff_series = pd.Series(days_diff.values, index=future_prices.index)
                    valid_days = days_diff_series[(days_diff_series >= target_days - 3) & (days_diff_series <= target_days + 3)]
                    if len(valid_days) > 0:
                        closest_idx = abs(valid_days - target_days).idxmin()
                        future_price = price_df.loc[closest_idx, 'Close']
                        return (future_price - price) / price * 100
                return np.nan
        
        return_1w = get_future_return(1)
        return_2w = get_future_return(2)
        return_3w = get_future_return(3)
        return_4w = get_future_return(4)
        
        results.append({
            'date': trade_date,
            'report_date': report_date,
            'price': price,
            'eps': eps,
            'pe': pe,
            'return_1w': return_1w,
            'return_2w': return_2w,
            'return_3w': return_3w,
            'return_4w': return_4w,
        })
        
        if len(results) % 500 == 0:
            print(f"  처리 중: {len(results)} 일일 데이터...")
    
    results_df = pd.DataFrame(results)
    print(f"\n✓ Calculated P/E for {len(results_df)} daily records")
    
    # 3. 통계 분석
    print("\n" + "=" * 80)
    print("통계 요약")
    print("=" * 80)
    print(f"평균 P/E: {results_df['pe'].mean():.2f}")
    print(f"중앙값 P/E: {results_df['pe'].median():.2f}")
    print(f"표준편차: {results_df['pe'].std():.2f}")
    print(f"최소값: {results_df['pe'].min():.2f}")
    print(f"최대값: {results_df['pe'].max():.2f}")
    
    # 4. 상관관계 분석
    print("\n" + "=" * 80)
    print("P/E와 미래 수익률 상관관계 (주별)")
    print("=" * 80)
    for weeks in [1, 2, 3, 4]:
        corr = results_df['pe'].corr(results_df[f'return_{weeks}w'])
        print(f"{weeks}주 상관관계: {corr:.4f}")
    
    # 5. 백분위별 수익률 분석
    print("\n" + "=" * 80)
    print("백분위별 수익률 분석 (4주)")
    print("=" * 80)
    
    percentile_results = calculate_percentile_returns(
        results_df['pe'],
        results_df['return_4w']
    )
    
    print(f"{'백분위':<15} {'P/E 범위':<25} {'평균 수익률':<15} {'샘플 수':<10}")
    print("-" * 80)
    for label, data in percentile_results.items():
        pe_range = data['pe_range']
        avg_return = data['avg_return']
        count = data['count']
        print(f"{label:<15} [{pe_range[0]:.2f}, {pe_range[1]:.2f}]{'':<10} {avg_return:>8.2f}%{'':<5} {count:>5}")
    
    # 6. 그래프 생성
    pe_series = pd.Series(results_df['pe'].values, index=results_df['date'])
    
    title = f"S&P 500 Forward P/E ({quarter_label_str})"
    fig = create_pe_chart(pe_series, title)
    
    # 파일명 생성
    start_str = f"m{abs(quarter_start)}" if quarter_start < 0 else f"{quarter_start}"
    end_str = f"{quarter_end-1}"
    file_suffix = f"q{start_str}_to_q{end_str}"
    output_path = OUTPUT_DIR / f'pe_{file_suffix}_chart.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Chart saved: {output_path}")
    
    # 7. 결과 저장
    output_csv = OUTPUT_DIR / f'pe_{file_suffix}_results.csv'
    results_df.to_csv(output_csv, index=False)
    print(f"✓ Results saved: {output_csv}")
    
    # 8. Q1분기 백분위별 수익률 분석
    results_df['quarter'] = results_df['date'].dt.quarter
    q1_data = results_df[results_df['quarter'] == 1]
    q1_pe = q1_data['pe'].dropna()
    q1_returns_4w = q1_data['return_4w'].dropna()
    
    if len(q1_pe) > 0:
        print("\n" + "=" * 80)
        print(f"Q1분기 백분위별 수익률 분석 ({quarter_label_str})")
        print("=" * 80)
        
        q1_percentile_results = calculate_percentile_returns(q1_pe, q1_returns_4w)
        
        print(f"{'백분위':<15} {'P/E 범위':<25} {'평균 수익률':<15} {'샘플 수':<10}")
        print("-" * 80)
        for label, data in q1_percentile_results.items():
            pe_range = data['pe_range']
            avg_return = data['avg_return']
            count = data['count']
            print(f"{label:<15} [{pe_range[0]:.2f}, {pe_range[1]:.2f}]{'':<10} {avg_return:>8.2f}%{'':<5} {count:>5}")
        
        correlation = q1_pe.corr(q1_returns_4w)
        print(f"\nP/E와 4주 수익률 상관관계: {correlation:.4f}")
    
    print("\n" + "=" * 80)
    print("분석 완료!")
    print("=" * 80)


if __name__ == "__main__":
    # 명령줄 인자로 분기 범위 지정
    # 예: python analyze_pe_flexible.py 0 4  → Q[0:4] = Q(0), Q(1), Q(2), Q(3)
    # 예: python analyze_pe_flexible.py 1 5  → Q[1:5] = Q(1), Q(2), Q(3), Q(4)
    # 예: python analyze_pe_flexible.py -3 1 → Q[-3:1] = Q(-3), Q(-2), Q(-1), Q(0)
    
    if len(sys.argv) >= 3:
        quarter_start = int(sys.argv[1])
        quarter_end = int(sys.argv[2])
    else:
        # 기본값: Q(1)+Q(2)+Q(3)+Q(4)
        quarter_start = 1
        quarter_end = 5
    
    main(quarter_start, quarter_end)

