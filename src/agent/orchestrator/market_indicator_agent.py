import asyncio

from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.market_breadth_agent import MarketBreadthAgent
from src.config import REPORT_LANGUAGE


class MarketIndicatorAgent(OrchestratorAgent):
    """
    Market indicator orchestrator.
    
    Combines multiple market indicators (breadth, sentiment, momentum, etc.).
    Extensible for additional indicators.
    """
    
    def __init__(self):
        """Initialize market indicator orchestrator."""
        super().__init__("market_indicator_orchestrator")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Add indicator sub-agents
        self.add_sub_agent(MarketBreadthAgent())
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
            You are a market indicator analyst synthesizing multiple technical and sentiment indicators.
            
            LANGUAGE REQUIREMENT:
            - ALL your responses MUST be in {REPORT_LANGUAGE}
            
            YOUR TASK:
            - Combine the provided market indicator analysis results
            - Assess overall market health and participation
            - Identify key trends, patterns, and divergences
            - Provide actionable insights based on indicator readings
            
            CRITICAL - CHART LINKS AND TABLES:
            - You MUST include ALL chart links and table structures from the original analyses
            - Please include the charts and tables as closely as possible to the original analyses
            - Do not mix up the requested periods for charts and tables
            """
        )


# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("Market Indicator Analysis")
        print("=" * 80)
        
        agent = MarketIndicatorAgent()
        result = await agent.run()
        print(result.content)
    
    asyncio.run(main())

