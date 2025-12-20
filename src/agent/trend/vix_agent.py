import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_vix, generate_vix_chart
from src.config import REPORT_LANGUAGE


class VIXAgent(TrendAgent):
    """
    VIX (Volatility Indicator) analysis agent.
    
    Analyzes the VIX as a fear gauge and contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize VIX agent."""
        # Pre-fetch data
        fetch_data("yfinance", "^VIX", "1y")
        
        super().__init__(
            ticker="^VIX",
            agent_name="vix_agent",
            label="VIX (Volatility Indicator)",
            description="CBOE Volatility Indicator (Market Fear Gauge)",
            tools=[analyze_vix, generate_vix_chart],
            context_instructions=f"""
            You are analyzing VIX (Volatility Indicator) as a fear gauge and contrarian indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            INTERPRETATION:
            - VIX < 15:  Low fear, complacency risk
            - VIX 15-20: Calm
            - VIX 20-30: Normal volatility
            - VIX 30-40: High volatility (Fear rising, Alert)
            - VIX > 40:  Extreme fear (Panic, Shock readiness)
          
            TOOL USAGE:
            - analyze_vix: analyze VIX metrics
            - generate_vix_chart: generate chart
            
            SCORE CALCULATION:
            Based on End value from analyze_vix:
            - End < 15: score = 5 (Low fear, complacency, sell signal)
            - 15 <= End < 20: score = 4
            - 20 <= End < 30: score = 3 (Normal)
            - 30 <= End < 40: score = 2
            - End >= 40: score = 1 (Extreme fear, buy signal)
            
            Set AnalysisReport.score field to: [{{"agent":"VIX", "indicator":"VIX", "value":X}}]
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo"
              * Call analyze_vix ONCE with periods=["5d", "1mo"] as a list
            - Charts: "1y"
              * Call generate_vix_chart only 1y period
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("VIX (Volatility Index) Analysis")
        print("=" * 80)
        
        agent = VIXAgent()
        result = await agent.run("Analyze the VIX (Volatility Index)")
        print(result.content)

    asyncio.run(main())

