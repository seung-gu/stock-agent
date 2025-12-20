import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_market_breadth, generate_market_breadth_chart
from src.config import REPORT_LANGUAGE


class MarketBreadthAgent(TrendAgent):
    """
    S&P 500 Market Breadth analysis agent.
    
    Analyzes the percentage of S&P 500 stocks trading above their 50-day and 200-day moving averages.
    """
    
    def __init__(self):
        """Initialize market breadth agent."""
        # Pre-fetch data
        fetch_data("investing", "S5TH", "5y")
        fetch_data("investing", "S5FI", "1y")
        
        super().__init__(
            ticker="S5TH",
            agent_name="market_breadth_agent",
            label="S&P 500 Market Breadth",
            description="S&P 500 stocks above 50-day and 200-day MA (이동 평균선 상회 종목 비중)",
            tools=[analyze_market_breadth, generate_market_breadth_chart],
            context_instructions=f"""
            You are a market breadth analyst specializing in S&P 500 participation metrics.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            ANALYSIS WORKFLOW:
            1. Analyze BOTH timeframes:
               - S5FI (50-day MA): analyze_market_breadth('S5FI', periods=['5d', '1mo', '3mo']) + generate_market_breadth_chart('S5FI', '1y')
               - S5TH (200-day MA): analyze_market_breadth('S5TH', periods=['5d', '1mo', '3mo']) + generate_market_breadth_chart('S5TH', '5y')
               * Note: analyze_market_breadth can accept multiple periods as a list if needed
            
            2. Market Breadth Framework
            
            Core Concept:
            - %Above50DMA = Speed (short-term momentum, moves quickly)
            - %Above200DMA = Direction (long-term trend, moves slowly)
            - "The 50DMA signals; the 200DMA confirms."
            
            Why Breadth Leads Index:
            - Market reversals begin in small-cap, high-beta stocks
            - Risk appetite returns → liquidity flows to smaller names first
            - Breadth improves before cap-weighted index responds
            - Large-caps (institutional flows) react later
            → Breadth = Process | Index = Outcome
            
            Market Cycle Pattern:
            ┌─────────────────────────────────────────────────────────────────────┐
            │ Late downturn: Large-caps hold up, breadth contracts (both weak)    │
            │ Early recovery: Small-caps rebound → %Above50DMA surges (leads)     │
            │ Trend confirmation: %Above200DMA rises → uptrend confirmed          │
            │ Late bull phase: Leadership narrows → %Above50DMA weakens (warning) │
            └─────────────────────────────────────────────────────────────────────┘
            
            Interpretation:
            - Rising %Above50DMA = Leading signal of market reversal
            - Weakening breadth = Internal exhaustion, early warning of top
            - This is a leading market indicator to catch top signals (emphasize this)
        
            TOOL USAGE:
            - analyze_market_breadth: analyze market breadth
            - generate_market_breadth_chart: generate market breadth chart
            
            CRITICAL:
            - MUST include BOTH charts (S5FI and S5TH)
            - This is a leading market indicator
            - Add reference links at end in markdown format:
              * [50-day MA Stock Breadth](https://www.investing.com/indices/s-p-500-stocks-above-50-day-average-chart)
              * [200-day MA Stock Breadth](https://www.investing.com/indices/sp-500-stocks-above-200-day-average-chart)
            
            SCORE CALCULATION:
            Call analyze_market_breadth for both S5FI and S5TH, then calculate scores based on End values:
            
            For each indicator:
            - End > 80: score = 5
            - End > 70: score = 4
            - End > 30: score = 3
            - End > 20: score = 2
            - End <= 20: score = 1
            
            Set AnalysisReport.score field to: 
            [{{"agent":"MarketBreadth", "indicator":"50-day MA(S5FI)", "value":X}}, 
            {{"agent":"MarketBreadth", "indicator":"200-day MA(S5TH)", "value":Y}}]
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("S&P 500 Market Breadth Analysis")
        print("=" * 80)
        
        agent = MarketBreadthAgent()
        result = await agent.run("Analyze the market breadth of S&P 500")
        print(result.content)
    
    asyncio.run(main())

