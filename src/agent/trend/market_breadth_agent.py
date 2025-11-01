import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_market_breadth, generate_market_breadth_chart
from src.config import REPORT_LANGUAGE


class MarketBreadthAgent(TrendAgent):
    """
    S&P 500 Market Breadth analysis agent.
    
    Analyzes the percentage of S&P 500 stocks trading above their 200-day moving average.
    """
    
    def __init__(self):
        """Initialize market breadth agent."""
        super().__init__(
            ticker="S5TH",
            agent_name="market_breadth_agent",
            label="S&P 500 Market Breadth",
            description="Percentage of S&P 500 stocks above 200-day MA (S&P 500 200일 이동 평균선 상회 종목 비중)",
            tools=[fetch_market_breadth, generate_market_breadth_chart],
            context_instructions=f"""
            You are a market breadth analyst specializing in S&P 500 participation metrics.
            
            LANGUAGE REQUIREMENT:
            - ALL your responses MUST be in {REPORT_LANGUAGE}
            
            YOUR TASK:
            1. Use fetch_market_breadth() to get current breadth data
            2. Use generate_market_breadth_chart() to create visualization
            3. Analyze the breadth reading:
               - Above 70%: Strong participation (bullish)
               - 50-70%: Healthy breadth (moderately bullish)
               - 30-50%: Weak breadth (moderately bearish)
               - Below 30%: Very weak participation (bearish)
            4. Assess market health and trend sustainability
            5. Identify divergences with major indices
            
            CRITICAL - INCLUDE CHART:
            - You MUST generate and include the breadth chart
            - Reference the chart when discussing trends
            
            ANALYSIS STRUCTURE:
            - Current breadth reading and interpretation
            - Historical context and trend
            - Market health assessment
            - Implications for sustainability
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("S&P 500 Market Breadth Analysis")
        print("=" * 80)
        
        agent = MarketBreadthAgent()
        result = await agent.run()
        print(result.content)
    
    asyncio.run(main())

