import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_OHLCV_data, generate_OHLCV_chart, analyze_SMA_data, \
analyze_disparity_data, generate_disparity_chart, generate_RSI_chart, analyze_RSI_data


class EquityTrendAgent(TrendAgent):
    """
    Equity-focused trend analysis agent for stock prices.
    
    Analyzes stock price movements with focus on investment opportunities,
    momentum, and technical patterns. Includes disparity analysis.
    """
    
    def __init__(self, ticker: str, label: str = None, description: str = None):
        """
        Initialize equity trend agent.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "TSLA", "^GSPC")
            label: Human-readable label (e.g., "S&P 500" for "^GSPC"). Defaults to ticker.
            description: Brief description of what this asset represents (optional)
        """
        self.ticker = ticker  # Store ticker before calling super
        agent_name = f"equity_agent_{ticker.replace('^', '').replace('-', '_')}"
        super().__init__(
            ticker=ticker,
            agent_name=agent_name,
            label=label,
            description=description,
            tools=[fetch_data, analyze_OHLCV_data, generate_OHLCV_chart, analyze_SMA_data, analyze_disparity_data, 
                   generate_disparity_chart, generate_RSI_chart, analyze_RSI_data],
            context_instructions="""
            EQUITY ANALYSIS FOCUS:
            You are an equity analyst specializing in stock or index price analysis.

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
            
            Technical Indicators:
            - Moving Averages (5, 20, 200) for trend analysis
              * 5, 20: Short-term trends
              * 200: Long-term trend and market psychology
            - 200-day Disparity for 5y period
            - RSI (14 window) for 1y period
            - Combine all the indicators to make a final decision.
              
            
            PERIOD REQUIREMENTS:
            - Tables: "5d", "1mo", "6mo", "1y"
            - Charts: "1mo", "1y" (use get_yf_data with include_chart=True)
            
            ADDITIONAL TOOLS:
            - analyze_SMA_data to analyze SMA data (Mandatory)
            - generate_disparity_chart (5y period) to generate disparity chart
            - generate_RSI_chart (14 window for 1y period) to generate RSI chart
            - analyze_RSI_data (14 window for 1y period) to analyze RSI data
            """
        )


# Usage examples
if __name__ == "__main__":
    async def main():
        print("\n" + "=" * 80)
        print("Example: Equity Analysis (NVDA)")
        print("=" * 80)
        # Example: Equity analysis (Stock)
        aapl_agent = EquityTrendAgent("ARKK")
        result = await aapl_agent.run("ARKK의 추세를 분석하고 투자 관점에서 해석해줘")
        print(result.content)
 
    asyncio.run(main())
