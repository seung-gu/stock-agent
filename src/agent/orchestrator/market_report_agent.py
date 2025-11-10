import asyncio
from dotenv import load_dotenv
from datetime import datetime

from src.agent.orchestrator.liquidity_agent import LiquidityAgent
from src.agent.orchestrator.broad_index_agent import BroadIndexAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.agent.orchestrator.market_health_agent import MarketHealthAgent
from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.config import REPORT_LANGUAGE


load_dotenv(override=True)


class MarketReportAgent(OrchestratorAgent):
    """
    Market report agent.
    
    Combines liquidity and equity analysis to generate comprehensive market reports.
    """
    
    def __init__(self):
        """Initialize market report agent."""
        super().__init__("market_report_agent")
      
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Add sub-agents using method chaining
        self.add_sub_agent(LiquidityAgent())\
            .add_sub_agent(MarketHealthAgent())\
            .add_sub_agent(BroadIndexAgent())\
            .add_sub_agent(EquityTrendAgent("IAU", label="iShares Gold Trust", description="Gold-tracking ETF"))\
            .add_sub_agent(EquityTrendAgent("QLD", label="ProShares Ultra QQQ", description="2x leveraged Nasdaq-100 ETF"))\
            .add_sub_agent(EquityTrendAgent("NVDA", label="NVIDIA"))\
            .add_sub_agent(EquityTrendAgent("MSFT", label="Microsoft"))\
            .add_sub_agent(EquityTrendAgent("AHR", label="American Health Care REITs", description="Provides access to a broad range of health care real estate investment trusts (REITs)"))\
            .add_sub_agent(EquityTrendAgent("SBUX", label="Starbucks"))\
            .add_sub_agent(EquityTrendAgent("JPM", label="JPMorgan Chase"))\
            .add_sub_agent(EquityTrendAgent("PLTR", label="Palantir Technologies"))\
            .add_sub_agent(EquityTrendAgent("COPX", label="Global X Copper Miners ETF", description="Provides access to a broad range of copper mining companies"))
  
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a market strategist synthesizing multiple analysis results.

        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        YOUR TASK:
        - Combine the provided analysis results into comprehensive market insights
        - Identify key patterns and correlations between different analyses
        - Provide strategic insights and recommendations
        - Maintain the unique characteristics of each analysis type
        - Today is {datetime.now().strftime("%Y-%m-%d")}
        - Include the week number of the current month and year in the report title
        
        DO NOT include any image links or tables in your response.
        """)
    

# Usage examples
if __name__ == "__main__":
    async def main():
        # Create orchestrator
        orchestrator = MarketReportAgent()
        
        # Run analysis
        result = await orchestrator.run()
        
        print("\n" + "=" * 80)
        print("📊 MARKET ANALYSIS RESULT")
        print("=" * 80)
        print(f"\n📄 Result: {result}")
        
    asyncio.run(main())
