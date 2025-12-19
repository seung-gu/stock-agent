from src.agent.base.orchestrator_agent import OrchestratorAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.config import REPORT_LANGUAGE


class PortfolioAgent(OrchestratorAgent):
    """
    Portfolio tracking orchestrator agent.
    
    Monitors and analyzes a collection of individual stocks and ETFs.
    """
    
    def __init__(self):
        """Initialize portfolio agent."""
        super().__init__("portfolio_orchestrator")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Add portfolio equity/ETF agents
        self.add_sub_agent(EquityTrendAgent("IAU", label="iShares Gold Trust", description="Gold-tracking ETF"))\
            .add_sub_agent(EquityTrendAgent("QLD", label="ProShares Ultra QQQ", description="2x leveraged Nasdaq-100 ETF"))\
            .add_sub_agent(EquityTrendAgent("NVDA", label="NVIDIA"))\
            .add_sub_agent(EquityTrendAgent("MSFT", label="Microsoft"))\
            .add_sub_agent(EquityTrendAgent("AHR", label="American Health Care REITs", description="Provides access to a broad range of health care real estate investment trusts (REITs)"))\
            .add_sub_agent(EquityTrendAgent("COPX", label="Global X Copper Miners ETF", description="Provides access to a broad range of copper mining companies"))
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a portfolio analyst synthesizing individual equity and ETF analyses.
        
        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}
        
        YOUR TASK:
        - Summarize the technical analysis results for each asset in the portfolio
        - Identify common patterns and trends across the portfolio
        - Highlight assets showing strong bullish or bearish signals
        - Provide portfolio-level insights and recommendations
        - Focus on actionable insights for portfolio management
        
        DO NOT include any image links or tables in your response.
        """)

