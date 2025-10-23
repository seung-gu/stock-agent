#!/usr/bin/env python3
"""TNX (10-Year Treasury Note) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class TNXAgent(TrendAgent):
    """Specialized agent for TNX (10-Year Treasury Note) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="^TNX",
            agent_name="tnx_agent",
            context_instructions="""
            You are a treasury analyst specializing in the TNX (10-Year Treasury Note) analysis.
            Please provide a detailed analysis of the TNX index and its trends.

            TREASURY YIELD ANALYSIS:
            - Rising yields = Tightening liquidity (negative for risk assets)
            - Falling yields = Loosening liquidity (positive for risk assets)
            - Yield volatility = Market uncertainty about liquidity conditions
            - Pay attention to integer percentage levels (3%, 4%, etc.) as psychological barriers
            - Assess implications for stock market, crypto, and risk assets

            TOOL USAGE:
            - Use get_yf_data("^TNX", period) for treasury yield data
            - Treasury yields come from Yahoo Finance (yfinance)
            """
        )
