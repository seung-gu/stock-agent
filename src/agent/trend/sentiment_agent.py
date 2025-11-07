import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_sentiment, generate_sentiment_chart
from src.config import REPORT_LANGUAGE


class SentimentAgent(TrendAgent):
    """
    AAII Investor Sentiment analysis agent.
    
    Analyzes the AAII Investor Sentiment (Bull-Bear Spread).
    """
    
    def __init__(self):
        """Initialize sentiment agent."""
        super().__init__(
            ticker="AAII_BULL_BEAR_SPREAD",
            agent_name="sentiment_agent",
            label="AAII Investor Sentiment",
            description="AAII Investor Sentiment (Bull-Bear Spread)",
            tools=[fetch_data, analyze_sentiment, generate_sentiment_chart],
            context_instructions=f"""
            You are a sentiment analyst specializing in AAII Investor Sentiment (Bull-Bear Spread).
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            ANALYSIS WORKFLOW:
            1. Fetch and analyze AAII Investor Sentiment (Bull-Bear Spread):
               - fetch_data + analyze_sentiment('1mo') + generate_sentiment_chart('5y')
            

            CRITICAL BUY SIGNALS (Contrarian Indicator):
            ┌──────────────────────────────────────────────────────────────────────┐
            │ Bull-Bear Spread ≤ -0.20 (-20%): 🟡 PRIMARY BUY SIGNAL               │
            │ → Extreme bearish sentiment = Major buying opportunity               │
            │                                                                      │
            │ Bull-Bear Spread ≤ -0.30 (-30%): 🔴 SECONDARY BUY SIGNAL             │
            │ → Panic selling zone = Strong accumulation opportunity               │
            └──────────────────────────────────────────────────────────────────────┘
            
            Interpretation:
            - Rising Bull-Bear Spread = Leading signal of bullish sentiment
            - Decreasing Bull-Bear Spread = Leading signal of bearish sentiment
            - Extreme negative values (-20% or below) = Contrarian buy signals
            - When sentiment is extremely bearish, market often bottoms
               
            TOOL USAGE:
            - fetch_data: fetch data from AAII (aaii)
            - analyze_sentiment: analyze sentiment
            - generate_sentiment_chart: generate sentiment chart
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("AAII Investor Sentiment Analysis")
        print("=" * 80)
        
        agent = SentimentAgent()
        result = await agent.run("Analyze the sentiment of AAII Investor Sentiment (Bull-Bear Spread)")
        print(result.content)
    
    asyncio.run(main())

