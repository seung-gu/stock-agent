#!/usr/bin/env python3
"""NFCI (National Financial Condition Index) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class NFCIAgent(TrendAgent):
    """Specialized agent for NFCI (National Financial Condition Index) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="NFCI",
            agent_name="nfci_agent",
            tools=[self._create_fred_tool()],
            context_instructions="""
            NFCI (National Financial Condition Index) Analysis:
            - NFCI = 0: Historical average financial conditions
            - NFCI > 0: Tighter conditions (credit stress, risk aversion)
            - NFCI < 0: Looser conditions (easy credit, risk appetite)
            - Rising NFCI = Financial conditions tightening (liquidity stress)
            - Falling NFCI = Financial conditions easing (liquidity improvement)
            
            PERIOD REQUIREMENTS:
            - Tables: "6mo", "1y", "2y"
            - Charts: "2y"
            """
        )
