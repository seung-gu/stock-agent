#!/usr/bin/env python3
"""DX=F (Dollar Index) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class DXAgent(TrendAgent):
    """Specialized agent for DX=F (Dollar Index) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="DX=F",
            agent_name="dx_agent",
            tools=[self._create_yfinance_tool()],
            context_instructions="""
            DX=F (Dollar Index) Analysis:
            - DX=F measures the value of the US dollar against a basket of foreign currencies
            - Rising DX=F = dollar strengthening (tightening liquidity, rising demand for dollars)
            - Falling DX=F = dollar weakening (loosening liquidity, falling demand for dollars)
            - Analyze how it affects the market and economy
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
            - Charts: "1mo","1y"
            """
        )
