from trend_research_base import TrendResearchBase


instructions = """
EQUITY ANALYSIS FOCUS:
You are an equity analyst specializing in stock price analysis.

Key Interpretations:
- Rising prices = Bullish sentiment, positive momentum, buying pressure
- Falling prices = Bearish sentiment, negative momentum, selling pressure
- Volatility = Market uncertainty and risk level
- Volume patterns for trend confirmation
- Support and resistance levels

Focus Areas:
- Price momentum and trend strength
- Market sentiment indicators
- Trading volume patterns
- Key technical levels (highs, lows)
- Risk/reward assessments for investors
- Entry/exit point considerations
"""

class EquityTrendAgent(TrendResearchBase):
    """
    Equity-focused trend analysis agent for stock prices.
    
    Analyzes stock price movements with focus on investment opportunities,
    momentum, and technical patterns.
    """
    
    def __init__(self, ticker: str):
        """
        Initialize equity trend agent.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")
        """
        agent_name = f"equity_agent_{ticker.replace('^', '').replace('-', '_')}"
        super().__init__(ticker, agent_name, instructions)


# Usage examples
if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("\n" + "=" * 80)
        print("Example: Equity Analysis (Apple)")
        print("=" * 80)
        # Example: Equity analysis (Stock)
        aapl_agent = EquityTrendAgent("AAPL")
        result = await aapl_agent.run("AAPL의 추세를 분석하고 투자 관점에서 해석해줘")
        print(result.final_output)
 
    asyncio.run(main())
