from datetime import datetime
from dotenv import load_dotenv
from agents import Runner, trace
from src.agent.orchestrator.liquidity_agent import LiquidityAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.agent.base.orchestrator_agent import OrchestratorAgent
import asyncio
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
            .add_sub_agent(EquityTrendAgent("MSFT"))
        
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
        
        DO NOT include any image links or tables in your response.
        """)
    
    async def run_sub_agents(self) -> list:
        """Run all sub-agents and return results"""
        return await asyncio.gather(*[agent.run("") for agent in self.sub_agents])
    
    async def run_synthesis(self, sub_agent_results: list) -> str:
        """Run synthesis on sub-agent results"""
        combined_input_parts = []
        for agent, result in zip(self.sub_agents, sub_agent_results):
            agent_name = agent.__class__.__name__
            combined_input_parts.append(f"{agent_name}:\n{result}")
        
        combined_input = "\n\n".join(combined_input_parts) + "\n\nPlease provide comprehensive market insights and strategic recommendations."
        
        synthesis_result = await Runner.run(self.synthesis_agent, input=combined_input)
        return synthesis_result.final_output if hasattr(synthesis_result, 'final_output') else str(synthesis_result)


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
