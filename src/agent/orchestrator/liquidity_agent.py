import asyncio
from src.agent.trend.tnx_agent import TNXAgent
from src.agent.trend.nfci_agent import NFCIAgent
from src.agent.trend.dx_agent import DXAgent
from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.config import REPORT_LANGUAGE


class LiquidityAgent(OrchestratorAgent):
    """
    Liquidity analysis orchestrator.
    
    Combines treasury yield analysis (TNX), financial conditions (NFCI), and currency strength (DX=F)
    to provide comprehensive liquidity insights.
    """
    
    def __init__(self):
        """Initialize liquidity agent with predefined TNX, NFCI, and DX=F agents."""
        super().__init__("liquidity_orchestrator")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Add sub-agents using method chaining
        self.add_sub_agent(TNXAgent())\
            .add_sub_agent(NFCIAgent())\
            .add_sub_agent(DXAgent())
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a liquidity analyst synthesizing multiple liquidity indicators.

        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        YOUR TASK:
        - Combine the provided liquidity analysis results
        - Identify key liquidity trends and patterns
        - Assess market implications for risk assets
        - Maintain the unique characteristics of each indicator
        
        CRITICAL - CHART LINKS AND TABLES:
        - You MUST include ALL chart links ([View Chart](sandbox:/path)) - count them and verify none are missing
        - Tables: You can summarize key findings, but include the full markdown table structure
        - Please include the charts and tables as closely as possible to the original analyses
        - Do not mix up the requested periods for charts and tables
        """
        )


# Usage examples
if __name__ == "__main__":
    async def main():
        # Example: Comprehensive liquidity analysis (TNX + NFCI + DX=F)
        print("=" * 80)
        print("Example: Liquidity Analysis (TNX + NFCI + DX=F)")
        print("=" * 80)
        liquidity_agent = LiquidityAgent()
        result = await liquidity_agent.run()
        print(result.content)
        
    asyncio.run(main())
