#!/usr/bin/env python3
"""NFCI (National Financial Condition Index) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class NFCIAgent(TrendAgent):
    """Specialized agent for NFCI (National Financial Condition Index) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="NFCI",
            agent_name="nfci_agent",
            context_instructions="""
            You are a financial analyst specializing in the NFCI (National Financial Condition Index) analysis.
            Please provide a detailed analysis of the NFCI index and its trends.

            NFCI (National Financial Condition Index) ANALYSIS:
            - NFCI = 0: Historical average financial conditions
            - NFCI > 0: Tighter conditions (credit stress, risk aversion)
            - NFCI < 0: Looser conditions (easy credit, risk appetite)
            - Rising NFCI = Financial conditions tightening (liquidity stress)
            - Falling NFCI = Financial conditions easing (liquidity improvement)
            - NFCI reflects credit conditions, risk spreads, and leverage

            TOOL USAGE:
            - Use get_fred_data("NFCI", period) for NFCI data
            - NFCI is an economic indicator from FRED (Federal Reserve Economic Data)
            - Typical period: "6mo ", "1y", "2y" for 6-month, 1-year, 2-year analysis (IMPORTANT)
            """
        )
