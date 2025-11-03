from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, ModelSettings

from src.agent.base.async_agent import AsyncAgent
from src.types.analysis_report import AnalysisReport
from src.config import REPORT_LANGUAGE

load_dotenv(override=True)


class TrendAgent(AsyncAgent):
    """
    Trend analysis agent for trend analysis with reusable tools and agent creation.
    """
    
    def __init__(self, ticker: str, agent_name: str, context_instructions: str, tools: list = [], label: str = None, description: str = None):
        """
        Initialize trend analysis agent with ticker.
        
        Args:
            ticker: Ticker symbol (e.g., "^TNX", "AAPL")
            agent_name: Agent name identifier (e.g., "liquidity_agent_TNX")
            context_instructions: Specialized analysis instructions
            tools: List of tools to use (optional)
            label: Human-readable label (e.g., "S&P 500" for "^GSPC"). Defaults to ticker.
            description: Brief description of what this asset represents (optional)
        """
        self.ticker = ticker
        self.label = label or ticker
        self.description = description
        self.context_instructions = context_instructions
        self.tools = tools
        self.output_type = AnalysisReport

        super().__init__(agent_name)
    
    def _create_agent(self) -> Agent:
        """
        Create the LLM agent with instructions and tools.
        
        Returns:
            Agent instance configured for trend analysis
        """
        instructions = f"""
        You are a specialized financial analyst for trend analysis.
        
        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        CRITICAL RULES:
        - NEVER try to create or output images directly in your text
        - ONLY use the provided tools to generate charts
        - DO NOT use markdown image syntax like ![image] in your responses
        - Charts will be automatically displayed by the system after you use the tools

        WORKFLOW:
        1. Analyze {self.label} (ticker: {self.ticker}){f' - {self.description}' if self.description else ''}
        2. Call appropriate tool for each period using {self.ticker}
        3. When calling the tools, always call the longest period first and then call the shorter periods in reverse order
        4. CRITICAL: Use fetch_data(source, symbol, period) once for the longest period FIRST to populate cache before analyzing other periods
        5. FORMAT OUTPUT AS MARKDOWN TABLE
        6. Include ALL chart links from tool responses in the order of the periods
        
        TOOL USAGE (for OHLCV data):
        - Use analyze_OHLCV_data(source, symbol, period) for table rows (no chart link returned)
        - Use generate_OHLCV_chart(source, symbol, period, label) to generate charts (returns "Chart saved: ...")
        - Tables and charts may require different period sets; call analyze_OHLCV_data and generate_OHLCV_chart independently
      
        OUTPUT FORMAT (REQUIRED):
        Start with a brief introduction.
        Then create a markdown table with analysis results for the requested periods in ascending order.
        
        | Period | Start | End | Change | High | Low | Volatility |
        |--------|-------|-----|--------|------|-----|------------|
        | [Period 1] | X.XXX | X.XXX | ±X.XX% | X.XXX | X.XXX | X.XXX |
        | [Period 2] | X.XXX | X.XXX | ±X.XX% | X.XXX | X.XXX | X.XXX |
        | [Period 3] | X.XXX | X.XXX | ±X.XX% | X.XXX | X.XXX | X.XXX |
        ...
        
        Then add chart links and comprehensive insights.

        CRITICAL - CHART LINKS: 
        - You MUST include the EXACT "Chart saved: /path/to/file.png" messages from ALL tools
        - Copy the FULL file path EXACTLY as returned (do NOT modify or shorten the path)
        - Use the format: [View Chart](sandbox:/full/exact/path.png)
        - ALL chart links MUST appear in the final output

        Today is {datetime.now().strftime("%Y-%m-%d")}.
        
        IMPORTANT - ANALYSIS REPORT STRUCTURE:
        You must return a structured AnalysisReport with:
        - title: Create a specific, descriptive title for {self.label} analysis
        - summary: Executive summary of key findings for {self.label}
        - content: The detailed analysis content above for {self.label}

        {self.context_instructions}
        """
        
        # Set tool_choice based on whether tools are available
        tool_choice = "required" if self.tools else "auto"
        
        return Agent(
            name=self.agent_name,
            instructions=instructions,
            model="gpt-4.1-mini",
            tools=self.tools,
            model_settings=ModelSettings(tool_choice=tool_choice),
            output_type=self.output_type
        )
        