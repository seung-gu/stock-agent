#!/usr/bin/env python3
"""TNX (10-Year Treasury Note) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_OHLCV_data, generate_OHLCV_chart, analyze_SMA_data

class TNXAgent(TrendAgent):
    """Specialized agent for TNX (10-Year Treasury Note) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="^TNX",
            agent_name="tnx_agent",
            label="10-Year Treasury Yield",
            tools=[fetch_data, analyze_OHLCV_data, generate_OHLCV_chart, analyze_SMA_data],
            context_instructions="""
            TNX (10-Year Treasury Note) Analysis:
            - Rising yields = Tightening liquidity (NEGATIVE for risk assets)
            - Falling yields = Loosening liquidity (POSITIVE for risk assets)
            - Prioritize longer timeframes over shorter ones
            - NEVER say "negative impact" when yields are falling long-term
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
            - Charts: "1mo","1y"
            
            ADDITIONAL TOOLS:
            - analyze_SMA_data to analyze SMA data (Mandatory)
            """
        )
