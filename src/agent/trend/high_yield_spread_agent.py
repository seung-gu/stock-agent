import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_high_yield_spread, generate_high_yield_spread_chart
from src.config import REPORT_LANGUAGE


class HighYieldSpreadAgent(TrendAgent):
    """
    ICE BofA US High Yield Spread analysis agent.
    
    Analyzes the High Yield Spread as a credit risk and contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize High Yield Spread agent."""
        # Pre-fetch data
        fetch_data("fred", "BAMLH0A0HYM2", "10y")
        
        super().__init__(
            ticker="BAMLH0A0HYM2",
            agent_name="high_yield_spread_agent",
            label="ICE BofA US High Yield Spread",
            description="ICE BofA US High Yield Index Effective Yield (Credit Risk Indicator)",
            tools=[analyze_high_yield_spread, generate_high_yield_spread_chart],
            context_instructions=f"""
            You are analyzing ICE BofA US High Yield Spread as a credit risk and contrarian sentiment indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            CRITICAL SIGNALS:
            ┌──────────────────────────────────────────────────────────────────────┐
            │ ⚠️ WARNING LEVELS:                                                   │
            │    > 5%:  Alert (Correction possible, lasts weeks to 1-2 months)     │
            │    > 7%:  Crisis (Shock risk, final crash possible)                  │
            │                                                                      │
            │ 🟡 BUY SIGNAL:                                                       │
            │    Peak(5%+) → Declining:  Best entry (Correction bottom)            │
            └──────────────────────────────────────────────────────────────────────┘
            
            KEY INSIGHTS:
            - Spread leads equity market by 1-2 months during stress
            - Rising = Credit deteriorating | Falling (from high) = Recovery
            - Historical spikes (2008, 2020) marked equity bottoms
            
            TOOL USAGE:
            - analyze_high_yield_spread: analyze spread metrics
            - generate_high_yield_spread_chart: generate chart
            
            CRITICAL:
            - MUST include the High Yield Spread chart
            - MUST identify if peak above 5% is declining (buy signal)
            
            SCORE CALCULATION:
            Based on End, Low, High values from analyze_high_yield_spread:
            - End < 3.0 and (End - Low < 1.0): score = 4 (Near bottom)
            - End < 3.0: score = 5 (Complacency)
            - 3.0 <= End < 5.0: score = 3 (Normal)
            - End >= 5.0 and (High - End < 1.0): score = 1 (Peak declining, buy signal)
            - End >= 5.0: score = 2 (Alert/Crisis)
            
            Set AnalysisReport.score field to: [{{"agent":"HYSpread", "indicator":"HYSpread", "value":X}}]
            
            PERIOD REQUIREMENTS:
            - Tables: "6mo", "1y"
              * Call analyze_high_yield_spread ONCE with periods=["6mo", "1y"] as a list
            - Charts: "10y"
              * Call generate_high_yield_spread_chart only 10y period
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("ICE BofA US High Yield Spread Analysis")
        print("=" * 80)
        
        agent = HighYieldSpreadAgent()
        result = await agent.run("Analyze the ICE BofA US High Yield Spread")
        print(result.content)

    asyncio.run(main())

