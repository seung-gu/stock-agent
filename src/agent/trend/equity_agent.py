from src.agent.base.trend_agent import TrendAgent


class EquityTrendAgent(TrendAgent):
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
        super().__init__(
            ticker=ticker,
            agent_name=agent_name,
            tools=[self._create_yfinance_tool()],
            context_instructions="""
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
            - Moving Averages (5, 20, 200) are important for trend analysis
            - 5, 20 are short-term trends, 200 is long-term trend
            - 50-day moving average is the 1-quarter average, so it can be used to understand how institutional investors are viewing the company's next quarter outlook
            - The 200-day moving average reveals market investors' buying/selling psychology (overheating or stagnation)
            - When the 200-day line is trending upward (important) and the stock price is above the 200-day line, there's a high probability of a major bull market 
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
            - Charts: "1mo","1y"
            """
        )


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
