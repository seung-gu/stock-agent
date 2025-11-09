import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_vix, generate_vix_chart
from src.config import REPORT_LANGUAGE


class VIXAgent(TrendAgent):
    """
    VIX (Volatility Index) analysis agent.
    
    Analyzes the VIX as a fear gauge and contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize VIX agent."""
        super().__init__(
            ticker="^VIX",
            agent_name="vix_agent",
            label="VIX (Volatility Index)",
            description="CBOE Volatility Index (Market Fear Gauge)",
            tools=[fetch_data, analyze_vix, generate_vix_chart],
            context_instructions=f"""
            You are analyzing VIX (Volatility Index) as a fear gauge and contrarian indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            INTERPRETATION:
            - VIX < 15:  Calm (Low fear, complacency risk)
            - VIX 15-20: Normal volatility
            - VIX 20-30: High volatility (Fear rising, Alert)   
            - VIX > 30:  Extreme fear (Panic, Shock readiness)
            
            TOOL USAGE:
            - fetch_data: fetch data from yfinance (yfinance)
            - analyze_vix: analyze VIX metrics
            - generate_vix_chart: generate chart
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo"
            - Charts: "1y"
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

