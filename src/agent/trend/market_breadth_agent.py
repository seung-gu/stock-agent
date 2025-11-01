import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_market_breadth, generate_market_breadth_chart
from src.config import REPORT_LANGUAGE


class MarketBreadthAgent(TrendAgent):
    """
    S&P 500 Market Breadth analysis agent.
    
    Analyzes the percentage of S&P 500 stocks trading above their 50-day and 200-day moving averages.
    """
    
    def __init__(self):
        """Initialize market breadth agent."""
        super().__init__(
            ticker="S5TH",
            agent_name="market_breadth_agent",
            label="S&P 500 Market Breadth",
            description="S&P 500 stocks above 50-day and 200-day MA (이동 평균선 상회 종목 비중)",
            tools=[fetch_market_breadth, generate_market_breadth_chart],
            context_instructions=f"""
            You are a market breadth analyst specializing in S&P 500 participation metrics.
            
            LANGUAGE REQUIREMENT:
            - ALL your responses MUST be in {REPORT_LANGUAGE}
            
            YOUR TASK:
            1. Analyze BOTH short-term (50-day MA) and long-term (200-day MA) breadth:
               - fetch_market_breadth(ma_period=50) for short-term trend (S5FI)
               - fetch_market_breadth(ma_period=200) for long-term trend (S5TH)
            2. Generate charts for BOTH periods:
               - generate_market_breadth_chart(ma_period=50) for S5FI
               - generate_market_breadth_chart(ma_period=200) for S5TH
            3. Interpret breadth levels:
               - Above 70%: Strong participation (bullish)
               - 50-70%: Healthy breadth (moderately bullish)
               - 30-50%: Weak breadth (moderately bearish)
               - Below 30%: Very weak participation (bearish)
            4. Compare short-term vs long-term trends:
               - Divergences: 50-day rising but 200-day falling (or vice versa)
               - Confirmation: Both moving in same direction
            5. Assess market health and trend sustainability
            6. Identify divergences with major indices
            7. This is a representative market leading indicator (Important to consider)
            
            CRITICAL - INCLUDE BOTH CHARTS:
            - You MUST generate and include BOTH 50-day and 200-day breadth charts
            - Reference both charts when discussing trends
            - Highlight differences between short-term and long-term trends
            
            ANALYSIS STRUCTURE:
            - Short-term breadth (50-day MA): Current reading and trend
            - Long-term breadth (200-day MA): Current reading and trend
            - Comparison: Divergences or confirmation between timeframes
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

