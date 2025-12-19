import asyncio

from src.agent.base.trend_agent import TrendAgent
from src.agent.tools.agent_tools import fetch_data, analyze_margin_debt, generate_margin_debt_chart
from src.config import REPORT_LANGUAGE


class MarginDebtAgent(TrendAgent):
    """
    FINRA Margin Debt analysis agent.
    
    Analyzes the FINRA Margin Debt as a contrarian sentiment indicator.
    """
    
    def __init__(self):
        """Initialize Margin Debt agent."""
        # Pre-fetch data
        fetch_data("finra", "MARGIN_DEBT_YOY", "10y")
        
        super().__init__(
            ticker="MARGIN_DEBT_YOY",
            agent_name="margin_debt_agent",
            label="FINRA Margin Debt (YoY %)",
            description="FINRA Margin Debt YoY % (Contrarian Sentiment Indicator)",
            tools=[analyze_margin_debt, generate_margin_debt_chart],
            context_instructions=f"""
            You are analyzing FINRA Margin Debt as a contrarian sentiment indicator.
            ALL responses MUST be in {REPORT_LANGUAGE}.

            CRITICAL SIGNALS (Contrarian Indicator):
            ┌──────────────────────────────────────────────────────────────────────┐
            │ 🔴 SELL SIGNALS (Market Overheating):                                │
            │    YoY > +50%:         1st SELL signal (Extreme leverage buildup)    │
            │    Peak → below 50%:   2nd SELL signal (Reversal confirmed)          │
            │                                                                      │
            │ 🟡 BUY SIGNALS (Market Oversold):                                    │
            │    YoY < -20%:         1st BUY signal (Deleveraging phase)           │
            │    YoY < -30%:         2nd BUY signal (Extreme deleveraging)         │
            │    Trough → above -20%: 3rd BUY signal (Reversal confirmed)          │
            └──────────────────────────────────────────────────────────────────────┘
            
            KEY INSIGHTS:
            - Rising margin debt = Increasing speculation and risk-taking
            - Extreme positive values (+50% or above) = Overheated market
            - Extreme negative values (-20% or below) = Deleveraging/capitulation
            - Trend reversals at extremes often precede major market moves
            - Margin debt leads market by ~1-3 months historically

            TOOL USAGE:
            - analyze_margin_debt: analyze margin debt
            - generate_margin_debt_chart: generate chart
            
            CRITICAL:
            - MUST include the Margin Debt chart
            
            SCORE CALCULATION:
            Based on End value (YoY %) from analyze_margin_debt:
            - End >= 40: score = 5 (Extreme leverage, sell signal)
            - End >= 20: score = 4 (Significant leverage)
            - End >= -20: score = 3 (Moderate)
            - End >= -30: score = 2
            - End < -30: score = 1 (Deleveraging, buy signal)
            
            Set AnalysisReport.score field to: [{{"agent":"MarginDebt", "indicator":"MarginDebt", "value":X}}]
            
            PERIOD REQUIREMENTS:
            - Tables: "6mo", "1y"
            - Charts: "10y"
            """
        )
        

# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("FINRA Margin Debt Analysis")
        print("=" * 80)
        
        agent = MarginDebtAgent()
        result = await agent.run("Analyze the FINRA Margin Debt")
        print(result.content)

    asyncio.run(main())

