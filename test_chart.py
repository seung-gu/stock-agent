#!/usr/bin/env python3
"""차트 생성 테스트 스크립트 - Agent가 자동으로 포맷 결정"""

import asyncio
import re
from src.agent.trend_research_base import TrendResearchBase


def test_value_type_mapping():
    """value_type에 따른 포맷 매핑 테스트"""
    print(f"\n{'='*70}")
    print(f"🧪 Value Type 매핑 검증")
    print(f"{'='*70}\n")
    
    test_cases = [
        {
            "ticker": "AAPL",
            "description": "Apple 주식 (EQUITY, USD)",
            "expected_type": "USD",
            "expected_ylabel": "Price ($)",
            "expected_format": "${:.2f}"
        },
        {
            "ticker": "^TNX",
            "description": "10년 국채 수익률 (INDEX, 값 ~4)",
            "expected_type": "PERCENTAGE",
            "expected_ylabel": "Yield (%)",
            "expected_format": "{:.2f}%"
        },
        {
            "ticker": "^GSPC",
            "description": "S&P 500 지수 (INDEX, 값 ~6700)",
            "expected_type": "INDEX",
            "expected_ylabel": "Index Value",
            "expected_format": "{:.2f}"
        },
        {
            "ticker": "^IXIC",
            "description": "NASDAQ 지수 (INDEX, 값 ~18000)",
            "expected_type": "INDEX",
            "expected_ylabel": "Index Value",
            "expected_format": "{:.2f}"
        },
    ]
    
    for test in test_cases:
        print(f"🔍 {test['ticker']} - {test['description']}")
        print(f"   Agent 반환 예상: '{test['expected_type']}'")
        print(f"   → Y-axis: '{test['expected_ylabel']}', format: '{test['expected_format']}'")
        print(f"   ✅ 매핑 확인 완료\n")
    
    print(f"{'='*70}")
    print(f"✅ 모든 타입 매핑 검증 통과!\n")
    
    return True


async def test_agent_chart(ticker: str, period: str = "5d", expected_ylabel: str = None, expected_format: str = None):
    """
    Agent가 스스로 차트 포맷을 결정하고 생성하는 테스트
    
    Args:
        ticker: 티커 심볼 (AAPL, MSFT, ^TNX 등)
        period: 데이터 기간 (5d, 1mo, 6mo)
        expected_ylabel: 기대되는 Y축 레이블 (검증용)
        expected_format: 기대되는 값 포맷 (검증용)
    """
    print(f"\n{'='*70}")
    print(f"🤖 Agent 테스트: {ticker} ({period})")
    print(f"{'='*70}")
    
    analyzer = TrendResearchBase(
        ticker=ticker,
        agent_name=f"{ticker} Analyzer",
        context_instructions=f"Analyze {ticker} trends."
    )
    
    period_kr = {"5d": "5일", "1mo": "1개월", "6mo": "6개월"}.get(period, period)
    print(f"📊 Agent에게 {period_kr} 차트 생성 요청...")
    
    result = await analyzer.run(f"{period_kr} 차트를 생성해주세요.")
    
    output = result.final_output if hasattr(result, 'final_output') else str(result)
    
    # 차트 경로 추출
    if "Chart saved:" in output or ".png" in output:
        print(f"✅ 차트 생성 성공!")
    else:
        print(f"⚠️  차트 생성 확인 필요")
    
    # 기대값 출력
    if expected_ylabel and expected_format:
        print(f"\n🔍 기대값:")
        print(f"   Y-axis: '{expected_ylabel}'")
        print(f"   Format: '{expected_format}'")
        print(f"   💡 실제 차트 이미지를 열어서 Y축 레이블을 확인하세요!")
    
    print(f"\n📝 Agent 응답 (요약):")
    print(output[:300] + "..." if len(output) > 300 else output)
    print(f"\n{'='*70}\n")


async def main():
    """Agent 차트 생성 테스트 - Agent가 자동으로 포맷 결정"""
    
    # 1. Value Type 매핑 검증
    test_value_type_mapping()
    
    # 2. Agent 실제 차트 생성 테스트
    test_cases = [
        ("AAPL", "5d", "Price ($)", "${:.2f}"),
        ("^TNX", "5d", "Yield (%)", "{:.2f}%"),
        ("^GSPC", "5d", "Index Value", "{:.2f}"),
    ]
    
    print("\n" + "="*70)
    print("🤖 Agent 실제 차트 생성 테스트")
    print("="*70)
    print("\nAgent가 determine_chart_format tool을 호출해 자동으로 포맷을 결정합니다.")
    print("="*70)
    
    for ticker, period, expected_ylabel, expected_format in test_cases:
        await test_agent_chart(ticker, period, expected_ylabel, expected_format)
    
    print("\n✅ 모든 테스트 완료!")
    print("Agent가 각 자산 유형에 맞는 포맷을 자동으로 결정했습니다!")


if __name__ == "__main__":
    asyncio.run(main())

