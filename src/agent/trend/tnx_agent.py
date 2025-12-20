#!/usr/bin/env python3
"""TNX (10-Year Treasury Note) Trend Analysis Agent"""

import asyncio
from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_OHLCV, generate_OHLCV_chart, analyze_SMA

class TNXAgent(TrendAgent):
    """Specialized agent for TNX (10-Year Treasury Note) analysis"""
    
    def __init__(self):
        # Pre-fetch data
        fetch_data("yfinance", "^TNX", "1y")
        
        super().__init__(
            ticker="^TNX",
            agent_name="tnx_agent",
            label="10-Year Treasury Yield",
            tools=[analyze_OHLCV, generate_OHLCV_chart, analyze_SMA],
            context_instructions="""
            TNX (10-Year Treasury Note) Analysis:
            - Rising yields = Tightening liquidity (NEGATIVE for risk assets)
            - Falling yields = Loosening liquidity (POSITIVE for risk assets)
            - Prioritize longer timeframes over shorter ones
            - NEVER say "negative impact" when yields are falling long-term
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
              * Call analyze_OHLCV ONCE with periods=["5d", "1mo", "6mo", "1y"] as a list
            - Charts: "1mo", "1y"
              * Call generate_OHLCV_chart separately for each period (one call per period)
            
            ADDITIONAL TOOLS:
            - analyze_SMA to analyze SMA data (window: 5, 50, 200)
            
            SCORE:
            This agent does NOT provide scoring. Do NOT set AnalysisReport.score field (leave it as default empty list []).
            """
        )
