#!/usr/bin/env python3
"""NFCI (National Financial Condition Index) Trend Analysis Agent"""
import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_NFCI, generate_NFCI_chart


class NFCIAgent(TrendAgent):
    """Specialized agent for NFCI (National Financial Condition Index) analysis"""
    
    def __init__(self):
        # Pre-fetch data
        fetch_data("fred", "NFCI", "2y")
        
        super().__init__(
            ticker="NFCI",
            agent_name="nfci_agent",
            label="National Financial Conditions Index",
            description="NFCI (National Financial Condition Index) analysis (금융 상황 종합 지수)",
            tools=[analyze_NFCI, generate_NFCI_chart],
            context_instructions="""
            NFCI (National Financial Condition Index) Analysis:
            - NFCI = 0: Historical average financial conditions
            - NFCI > 0: Tighter conditions (credit stress, risk aversion)
            - NFCI < 0: Looser conditions (easy credit, risk appetite)
            - Rising NFCI = Financial conditions tightening (liquidity stress)
            - Falling NFCI = Financial conditions easing (liquidity improvement)
            
            DATA SOURCE:
            - Data is pre-fetched from FRED
            - Use analyze_NFCI and generate_NFCI_chart (no source parameter needed)
            
            PERIOD REQUIREMENTS:
            - Tables: "6mo", "1y", "2y"
            - Charts: "2y"
            
            SCORE:
            This agent does NOT provide scoring. Do NOT set AnalysisReport.score field (leave it as default empty list []).
            """
        )


# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("NFCI (National Financial Condition Index) Analysis")
        print("=" * 80)
        
        agent = NFCIAgent()
        result = await agent.run("Analyze the NFCI (National Financial Condition Index)")
        print(result.content)

    asyncio.run(main())
    