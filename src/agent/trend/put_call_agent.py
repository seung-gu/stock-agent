import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_put_call, generate_put_call_chart
from src.config import REPORT_LANGUAGE


class PutCallAgent(TrendAgent):
    """
    CBOE Equity Put/Call Ratio analysis agent.
    
    Analyzes the CBOE Equity Put/Call Ratio as a contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize Put/Call Ratio agent."""
        # Pre-fetch data
        fetch_data("ycharts", "CBOE_PUT_CALL_EQUITY", "1y")
        
        super().__init__(
            ticker="CBOE_PUT_CALL_EQUITY",
            agent_name="put_call_agent",
            label="CBOE Equity Put/Call Ratio",
            description="CBOE Equity Put/Call Ratio (Contrarian Sentiment Indicator)",
            tools=[analyze_put_call, generate_put_call_chart],
            context_instructions=f"""
            You are analyzing CBOE Equity Put/Call Ratio as a contrarian sentiment indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.
            
            ANALYSIS WORKFLOW:
            1. Analyze Put/Call Ratio:
               - analyze_put_call('1mo') + generate_put_call_chart('6mo')
            
            INTERPRETATION (Contrarian Indicator):
            ┌──────────────────────────────────────────────────────────────────┐
            │ Ratio < 0.7:  Bullish sentiment (Calls > Puts)                   │
            │ → Too much optimism, potential correction ahead                  │
            │                                                                  │
            │ Ratio 0.7-1.0: Neutral to slightly bearish                       │
            │                                                                  │
            │ Ratio > 1.0:  Bearish sentiment (Puts > Calls)                   │
            │ → Fear/hedging increases                                         │
            │                                                                  │
            │ 🟡 Ratio > 1.0: FEAR → 1st BUY signal                            │
            │    Ratio > 1.5: EXTREME FEAR → 2nd BUY signal                    │
            │ 🔴 Ratio < 0.5: GREED → 1st SELL signal                          │
            └──────────────────────────────────────────────────────────────────┘
            
            KEY INSIGHTS:
            - Rising ratio = Increasing bearish hedging (puts buying up)
            - Falling ratio = Decreasing fear, more bullish positioning
            - Extreme values often mark market turning points
  
            TOOL USAGE:
            - analyze_put_call: analyze ratio
            - generate_put_call_chart: generate chart
            
            CRITICAL:
            - MUST include the Put/Call Ratio chart
            
            SCORE CALCULATION:
            Based on End value from analyze_put_call:
            - End < 0.4: score = 5 (Extreme greed, sell signal)
            - 0.4 <= End < 0.5: score = 4
            - 0.5 <= End < 1.0: score = 3 (Neutral)
            - 1.0 <= End < 1.2: score = 2
            - End >= 1.2: score = 1 (Extreme fear, buy signal)
            
            Set AnalysisReport.score field to: [{{"agent":"PutCall", "indicator":"PutCall", "value":X}}]
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("CBOE Equity Put/Call Ratio Analysis")
        print("=" * 80)
        
        agent = PutCallAgent()
        result = await agent.run("Analyze the CBOE Equity Put/Call Ratio")
        print(result.content)
    
    asyncio.run(main())

