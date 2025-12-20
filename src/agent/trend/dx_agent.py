#!/usr/bin/env python3
"""DX=F (Dollar Index) Trend Analysis Agent"""

import asyncio
from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_OHLCV, generate_OHLCV_chart, analyze_SMA

class DXAgent(TrendAgent):
    """Specialized agent for DX=F (Dollar Indicator) analysis"""
    
    def __init__(self):
        # Pre-fetch data
        fetch_data("yfinance", "DX=F", "1y")
        
        super().__init__(
            ticker="DX=F",
            agent_name="dx_agent",
            label="US Dollar Indicator",
            tools=[analyze_OHLCV, generate_OHLCV_chart, analyze_SMA],
            context_instructions="""
            DX=F (Dollar Indicator) Analysis:
            - DX=F measures the value of the US dollar against a basket of foreign currencies
            - Rising DX=F = dollar strengthening (tightening liquidity, rising demand for dollars)
            - Falling DX=F = dollar weakening (loosening liquidity, falling demand for dollars)
            - Analyze how it affects the market and economy
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
              * Call analyze_OHLCV ONCE with periods=["5d", "1mo", "6mo", "1y"] as a list
            - Charts: "1mo", "1y"
              * Call generate_OHLCV_chart only 1mo and 1y periods
            
            ADDITIONAL TOOLS:
            - analyze_SMA to analyze SMA data (window: 5, 50, 200)
            
            SCORE:
            This agent does NOT provide scoring. Do NOT set AnalysisReport.score field (leave it as default empty list []).
            """
        )

    