import asyncio
from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import analyze_market_pe, generate_market_pe_chart
from src.config import REPORT_LANGUAGE


class MarketPEAgent(TrendAgent):
    """
    S&P 500 Market P/E ratio analysis agent.
    
    Analyzes the trailing P/E ratio of S&P 500 using factset_report_analyzer.
    """
    
    def __init__(self):
        """Initialize market P/E ratio agent."""
        super().__init__(
            ticker="",
            agent_name="market_pe_agent",
            label="S&P 500 Market P/E Ratio",
            description="S&P 500 trailing P/E ratio",
            tools=[analyze_market_pe, generate_market_pe_chart],
            context_instructions=f"""
            You are a market valuation analyst specializing in S&P 500 P/E ratio analysis.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            ANALYSIS WORKFLOW:
            1. Call analyze_market_pe('trailing', '1y') and analyze_market_pe('forward', '1y')
            2. Analyze trailing and forward both in the table format
            3. Call generate_market_pe_chart('trailing') and generate_market_pe_chart('forward')
            
            INTERPRETATION:
            - This is a leading market indicator to catch bottom signals (emphasize this)
            
            SCORE CALCULATION:
            - Extract rank percentages from both analyze_market_pe outputs (look for "Current Rank: X.X%")
            - Calculate average_rank = (trailing_rank + forward_rank) / 2
            - Compare average_rank to thresholds EXACTLY:
              * If average_rank < 7: Score = 1
              * If 7 <= average_rank < 20: Score = 2
              * If 20 <= average_rank < 80: Score = 3
              * If 80 <= average_rank < 93: Score = 4 (NOTE: 93 is NOT included, so 91.4% = Score 4)
              * If average_rank >= 93: Score = 5 (ONLY if 93.0 or higher)
            - Example: 92.4% is LESS than 93, so it must be Score 4, NOT Score 5
            - Set AnalysisReport.score to: [{{"agent":"MarketPE", "indicator":"P/E Ratio Rank", "value":X}}]
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("S&P 500 Market P/E Ratio Analysis")
        print("=" * 80)
        
        agent = MarketPEAgent()
        result = await agent.run("Analyze the S&P 500 market P/E ratio")
        print(result.content)
    
    asyncio.run(main())

