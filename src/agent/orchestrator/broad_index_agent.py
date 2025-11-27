import asyncio

from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.agent.trend.market_breadth_agent import MarketBreadthAgent
from src.agent.trend.market_pe_agent import MarketPEAgent
from src.config import REPORT_LANGUAGE


class BroadIndexAgent(OrchestratorAgent):
    """
    Broad index analysis orchestrator.
    
    Combines broad index analysis to provide comprehensive broad index insights.
    """
    
    def __init__(self):
        """Initialize broad index agent with predefined broad index agents."""
        super().__init__("broad_index_orchestrator")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Add sub-agents using method chaining
        self.add_sub_agent(EquityTrendAgent("^GSPC", label="S&P 500"))\
            .add_sub_agent(EquityTrendAgent("^IXIC", label="Nasdaq Composite"))\
            .add_sub_agent(EquityTrendAgent("^DJI", label="Dow Jones Industrial Average"))\
            .add_sub_agent(MarketBreadthAgent())\
            .add_sub_agent(MarketPEAgent())
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a broad market analyst synthesizing major index performance and market indicators.

        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        YOUR TASK:
        - Combine analysis from major indices (S&P 500, Nasdaq, Dow Jones)
        - Integrate market indicator analysis (breadth, sentiment, etc.)
        - Identify trends, patterns, and divergences across indices
        - Assess market health: Do indicators confirm index movements?
        - Look for warning signs (e.g., indices rising but breadth weakening)
        - Provide actionable insights on market direction and risk
        - Extract individual scores and sum to calculate average composite score (1.0 to 5.0)
        
        CRITICAL - CONTENT REQUIREMENTS:
        - You MUST include ALL chart links ([View Chart](sandbox:/path)) - count them and verify none are missing
        - You MUST include ALL reference links ([text](https://...))
        - Tables: You can summarize key findings, but include the full markdown table structure
        - If output is too long, summarize analysis text but NEVER omit chart/reference links
        
        AVERAGE COMPOSITE SCORE INTERPRETATION (range: 1.0-5.0):
        - Score <= 1.5: 🟢 STRONG_BUY (Extreme fear/panic)
        - 1.5 < Score <= 2.5: 🟡 BUY (Oversold)
        - 2.5 < Score <= 3.5: ⚪ NEUTRAL (Normal range)
        - 3.5 < Score <= 4.5: 🟠 CAUTION (Overheating)
        - Score > 4.5: 🔴 STRONG_SELL (Extreme greed/bubble)
        
        SCORE FIELD:
        Set AnalysisReport.score = [{{"agent": "BroadIndex", "indicator": "Composite", "value": (average of 4 sub-agent scores)}}]
        
        OUTPUT FORMAT (translate all headings to {REPORT_LANGUAGE}):
        
        ## Composite Score (S&P 500)
        Extract 5 scores: S&P 500 (RSI, Disparity) + MarketBreadth (S5FI, S5TH) + P/E Ratio Rank

        | Indicator | Score | Interpretation |
        | S&P 500 RSI(14) | X | ... |
        | S&P 500 Disparity(200) | Y | ... |
        | MarketBreadth 50-day MA | A | ... |
        | MarketBreadth 200-day MA | B | ... |
        | P/E Ratio Rank | C | ... |
        [Summary table with all indicator scores and interpretation with average score at the bottom and signal]
        
        ## 1. [Indicator Name]
        [Brief analysis]
        [Chart link from sub-agent]
        [Data table from sub-agent]
        [Reference links from sub-agent] (Optional)
        
        ## 2. [Next Indicator]
        [Brief analysis]
        [Chart link]
        [Data table]
        [Reference links] (Optional)
        
        ... (repeat for all indicators)
        
        ## Strategic Interpretation
        [Overall interpretation based on composite score]

        CRITICAL: Place charts/tables/links RIGHT AFTER each indicator's analysis, NOT at the end.
        COPY & PASTE exact chart paths and tables from sub-agents.
        """
        )


# Usage examples
if __name__ == "__main__":
    async def main():
        # Example: Comprehensive broad index analysis (^GSPC + ^IXIC + ^DJI)
        print("=" * 80)
        print("Example: Broad Index Analysis (^GSPC + ^IXIC + ^DJI)")
        print("=" * 80)
        broad_index_agent = BroadIndexAgent()
        result = await broad_index_agent.run()
        print(result.content)
        
    asyncio.run(main())
