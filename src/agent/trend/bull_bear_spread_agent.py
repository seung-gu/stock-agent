import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_bull_bear_spread, generate_bull_bear_spread_chart
from src.config import REPORT_LANGUAGE


class BullBearSpreadAgent(TrendAgent):
    """
    AAII Bull-Bear Spread analysis agent.
    
    Analyzes the AAII Bull-Bear Spread as a contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize Bull-Bear Spread agent."""
        # Pre-fetch data
        fetch_data("aaii", "AAII_BULL_BEAR_SPREAD", "5y")
        
        super().__init__(
            ticker="AAII_BULL_BEAR_SPREAD",
            agent_name="bull_bear_spread_agent",
            label="AAII Bull-Bear Spread",
            description="AAII Investor Sentiment Survey (Bull-Bear Spread)",
            tools=[analyze_bull_bear_spread, generate_bull_bear_spread_chart],
            context_instructions=f"""
            You are analyzing AAII Bull-Bear Spread as a contrarian sentiment indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            CRITICAL BUY SIGNALS (Contrarian Indicator):
            ┌──────────────────────────────────────────────────────────────────────┐
            │ Bull-Bear Spread ≤ -0.20 (-20%): 🟡 PRIMARY BUY SIGNAL               │
            │ → Extreme bearish sentiment = Major buying opportunity               │
            │                                                                      │
            │ Bull-Bear Spread ≤ -0.30 (-30%): 🔴 SECONDARY BUY SIGNAL             │
            │ → Panic selling zone = Strong accumulation opportunity               │
            └──────────────────────────────────────────────────────────────────────┘
            
            INTERPRETATION:
            - Rising spread = Bullish sentiment increasing
            - Falling spread = Bearish sentiment increasing
            - Extreme negative values (≤-20%) = Contrarian buy signals
            - Market often bottoms when sentiment is extremely bearish
               
            TOOL USAGE:
            - analyze_bull_bear_spread: analyze spread metrics
            - generate_bull_bear_spread_chart: generate chart
            
            CRITICAL:
            - MUST include the Bull-Bear Spread chart
            
            SCORE CALCULATION:
            Based on End value from analyze_bull_bear_spread:
            - End > 0.3: score = 5 (Extreme bullish, sell signal)
            - 0.2 < End <= 0.3: score = 4
            - -0.2 <= End <= 0.2: score = 3 (Neutral)
            - -0.3 <= End < -0.2: score = 2
            - End < -0.3: score = 1 (Extreme bearish, buy signal)
            
            Set AnalysisReport.score field to: [{{"agent":"BullBear", "indicator":"BullBear", "value":X}}]
          
            PERIOD REQUIREMENTS:
            - Tables: "1mo"
            - Charts: "5y"
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("AAII Bull-Bear Spread Analysis")
        print("=" * 80)
        
        agent = BullBearSpreadAgent()
        result = await agent.run("Analyze the AAII Bull-Bear Spread")
        print(result.content)
    
    asyncio.run(main())

