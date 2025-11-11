import asyncio

from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.bull_bear_spread_agent import BullBearSpreadAgent
from src.agent.trend.put_call_agent import PutCallAgent
from src.agent.trend.margin_debt_agent import MarginDebtAgent
from src.agent.trend.high_yield_spread_agent import HighYieldSpreadAgent
from src.agent.trend.vix_agent import VIXAgent
from src.config import REPORT_LANGUAGE


class MarketHealthAgent(OrchestratorAgent):
    """
    Market Health Monitor - Contrarian Indicator Synthesizer.
    
    Synthesizes 5 contrarian indicators to gauge market extremes and health.
    """
    
    def __init__(self):
        """Initialize market health agent with contrarian indicator agents."""
        super().__init__("market_health_agent")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        self.add_sub_agent(BullBearSpreadAgent())\
            .add_sub_agent(PutCallAgent())\
            .add_sub_agent(MarginDebtAgent())\
            .add_sub_agent(HighYieldSpreadAgent())\
            .add_sub_agent(VIXAgent())
        
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a market health analyst synthesizing contrarian indicators.
        ALL responses MUST be in {REPORT_LANGUAGE}.
        
        YOUR TASK:
        - Combine analysis from each sub-agent
        - Identify trends, patterns, and divergences across indicators
        - Assess market health: Do indicators confirm each other's movements?
        - Look for warning signs (e.g., indicators rising but others weakening)
        - Extract individual scores and sum to calculate average composite score (0 to 5)
        - Present results in clear summary table with strategic interpretation
        
        AVERAGE COMPOSITE SCORE INTERPRETATION:
        - Score < 1: 🟢 STRONG_BUY (Extreme fear/panic)
        - 1 <= Score < 2: 🟡 BUY (Oversold)
        - 2 <= Score < 3: ⚪ NEUTRAL (Normal range)
        - 3 <= Score < 4: 🟠 CAUTION (Overheating)
        - 4 <= Score: 🔴 STRONG_SELL (Extreme greed/bubble)
        
        OUTPUT FORMAT (MUST FOLLOW):
        
        ## Market Health Score Summary
        [Summary table with all indicator scores and interpretation]
        
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


# Usage example
if __name__ == "__main__":
    async def main():
        print("=" * 80)
        print("Market Health Monitor Analysis")
        print("=" * 80)
        
        agent = MarketHealthAgent()
        result = await agent.run()
        print(result.content)
    
    asyncio.run(main())
