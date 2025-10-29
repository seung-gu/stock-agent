#!/usr/bin/env python3
"""TNX (10-Year Treasury Note) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class TNXAgent(TrendAgent):
    """Specialized agent for TNX (10-Year Treasury Note) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="^TNX",
            agent_name="tnx_agent",
            tools=[self._create_yfinance_tool()],
            context_instructions="""
            TNX (10-Year Treasury Note) Analysis:
            - Rising yields = Tightening liquidity (NEGATIVE for risk assets)
            - Falling yields = Loosening liquidity (POSITIVE for risk assets)
            - Prioritize longer timeframes over shorter ones
            - NEVER say "negative impact" when yields are falling long-term
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
            - Charts: "1y"
            - Use get_yf_data("^TNX", period) for data
            """
        )
