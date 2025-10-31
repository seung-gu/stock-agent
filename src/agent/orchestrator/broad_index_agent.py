import asyncio

from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.equity_agent import EquityTrendAgent
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
            .add_sub_agent(EquityTrendAgent("^DJI", label="Dow Jones Industrial Average"))
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a broad index (^GSPC(S&P 500), ^IXIC(NASDAQ), ^DJI(Dow Jones Industrial Average)) analyst synthesizing multiple broad index analysis results.

        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        YOUR TASK:
        - Combine the provided broad index analysis results
        - Identify key broad index trends and patterns
        - Assess market implications for risk assets
        - Maintain the unique characteristics of each indicator
        
        CRITICAL - CHART LINKS AND TABLES:
        - You MUST include ALL chart links and table structures from the original analyses
        - Please include the charts and tables as closely as possible to the original analyses
        - Do not mix up the requested periods for charts and tables
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
