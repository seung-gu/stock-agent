#!/usr/bin/env python3
"""DX=F (Dollar Index) Trend Analysis Agent"""

from src.agent.base.trend_agent import TrendAgent

class DXAgent(TrendAgent):
    """Specialized agent for DX=F (Dollar Index) analysis"""
    
    def __init__(self):
        super().__init__(
            ticker="DX=F",
            agent_name="dx_agent",
            context_instructions="""
            You are a currency analyst specializing in the DX=F (Dollar Index) analysis.
            Please provide a detailed analysis of the DX=F index and its trends.
            
            DX=F (Dollar Index) ANALYSIS:
            - DX=F is a currency index that measures the value of the US dollar against a basket of other currencies
            - Rising DX=F means dollar strengthening, but this can be a sign of tightening liquidity or rising demand for dollars.
            - Falling DX=F means dollar weakening, but this can be a sign of loosening liquidity or falling demand for dollars.
            
            But please give more insights on how it affects the market and the economy.
            
            TOOL USAGE:
            - Use get_yf_data("DX=F", period) for DX=F data
            - DX=F is a currency index from Yahoo Finance (yfinance)
            - Typical period: "5d", "1mo", "6mo" for 5-day, 1-month, 6-month analysis
            """
        )
