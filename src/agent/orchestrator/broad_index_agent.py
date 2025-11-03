import asyncio

from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.agent.trend.market_breadth_agent import MarketBreadthAgent
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
            .add_sub_agent(MarketBreadthAgent())
        
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
            
            CRITICAL - CONTENT REQUIREMENTS:
            - You MUST include ALL chart links ([View Chart](sandbox:/path)) - count them and verify none are missing
            - You MUST include ALL reference links ([text](https://...))
            - Tables: You can summarize key findings, but include the full markdown table structure
            - If output is too long, summarize analysis text but NEVER omit chart/reference links
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
