#!/usr/bin/env python3
"""테스트용 이미지 생성"""

import matplotlib.pyplot as plt
import numpy as np
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans', 'Malgun Gothic', 'AppleGothic', 'NanumGothic']
plt.rcParams['axes.unicode_minus'] = False

def create_test_charts():
    """테스트용 차트 이미지들 생성"""
    
    # 테스트 디렉토리 생성
    test_dir = "/tmp/test_charts"
    os.makedirs(test_dir, exist_ok=True)
    
    # 1. TNX 5일 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 5, 5)
    y = 4.0 + 0.1 * np.sin(x) + np.random.normal(0, 0.02, 5)
    plt.plot(x, y, 'b-', linewidth=2, marker='o')
    plt.title('TNX 5일 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('수익률 (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/TNX_5_days_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 2. TNX 1개월 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 30, 30)
    y = 4.1 + 0.2 * np.sin(x/5) + np.random.normal(0, 0.05, 30)
    plt.plot(x, y, 'g-', linewidth=2, marker='s')
    plt.title('TNX 1개월 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('수익률 (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/TNX_1_month_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 3. TNX 6개월 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 180, 180)
    y = 4.4 - 0.4 * (x/180) + 0.1 * np.sin(x/20) + np.random.normal(0, 0.1, 180)
    plt.plot(x, y, 'r-', linewidth=2)
    plt.title('TNX 6개월 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('수익률 (%)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/TNX_6_months_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 4. AAPL 5일 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 5, 5)
    y = 250 + 10 * np.sin(x) + np.random.normal(0, 2, 5)
    plt.plot(x, y, 'purple', linewidth=2, marker='o')
    plt.title('AAPL 5일 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('주가 ($)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/AAPL_5_days_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 5. AAPL 1개월 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 30, 30)
    y = 255 + 5 * np.sin(x/5) + np.random.normal(0, 3, 30)
    plt.plot(x, y, 'orange', linewidth=2, marker='s')
    plt.title('AAPL 1개월 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('주가 ($)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/AAPL_1_month_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    # 6. AAPL 6개월 차트
    plt.figure(figsize=(10, 6))
    x = np.linspace(0, 180, 180)
    y = 200 + 60 * (x/180) + 10 * np.sin(x/20) + np.random.normal(0, 5, 180)
    plt.plot(x, y, 'darkgreen', linewidth=2)
    plt.title('AAPL 6개월 차트 (테스트)', fontsize=14)
    plt.xlabel('일수')
    plt.ylabel('주가 ($)')
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{test_dir}/AAPL_6_months_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 테스트 차트 이미지 생성 완료: {test_dir}")
    return test_dir

if __name__ == "__main__":
    create_test_charts()
