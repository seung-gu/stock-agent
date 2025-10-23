from datetime import datetime
from agents.result import T
from dotenv import load_dotenv
from agents import Agent, function_tool, ModelSettings

from src.agent.base.async_agent import AsyncAgent
from src.utils.data_sources import get_data_source
from src.config import REPORT_LANGUAGE

load_dotenv(override=True)


class TrendAgent(AsyncAgent):
    """
    Trend analysis agent for trend analysis with reusable tools and agent creation.
    """
    
    def __init__(self, ticker: str, agent_name: str, context_instructions: str):
        """
        Initialize trend analysis agent with ticker.
        
        Args:
            ticker: Ticker symbol (e.g., "^TNX", "AAPL")
            agent_name: Agent name identifier (e.g., "liquidity_agent_TNX")
            context_instructions: Specialized analysis instructions
        """
        self.ticker = ticker
        self.context_instructions = context_instructions

        super().__init__(agent_name)
    
    def _setup(self):
        """Set up instance attributes before agent creation."""
        self.yfinance_tool = self._create_yfinance_tool()
        self.fred_tool = self._create_fred_tool()
    
    def _create_yfinance_tool(self):
        """Create yfinance data tool."""
        @function_tool
        async def get_yf_data(symbol: str, period: str) -> str:
            """
            Get stock, ETF, or treasury data from Yahoo Finance.
            
            Args:
                symbol: Ticker symbol (e.g., ^TNX, AAPL, SPY)
                period: Time period (5d, 1mo, 6mo)
                
            Returns:
                Analysis with price data and chart link
            """
            try:
                source = get_data_source("yfinance")
                data = await source.fetch_data(symbol, period)
                analysis = source.get_analysis(data, period)
                chart_info = await source.create_chart(data, symbol, period)
                
                period_name = {"5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months"}.get(period, period)
                
                output = f"""{period_name} Analysis ({symbol}):
                        - Start: {analysis['start']:.3f}
                        - End: {analysis['end']:.3f}
                        - Change: {analysis['change_pct']:+.2f}%
                        - High: {analysis['high']:.3f}
                        - Low: {analysis['low']:.3f}
                        - Volatility: {analysis['volatility']:.3f}

                        {chart_info}"""
                
                return output
            except Exception as e:
                return f"Error fetching data for {symbol}: {str(e)}"
        
        return get_yf_data
    
    def _create_fred_tool(self):
        """Create FRED economic data tool."""
        @function_tool
        async def get_fred_data(indicator: str, period: str = "6mo") -> str:
            """
            Get economic indicator data from FRED (Federal Reserve Economic Data).
            
            Args:
                indicator: FRED indicator code (e.g., NFCI, DFF, T10Y2Y, UNRATE)
                period: Time period (6mo, 1y, 2y) - default 6mo (IMPORTANT)
                
            Returns:
                Analysis with indicator data and chart link
            """
            try:
                source = get_data_source("fred")
                data = await source.fetch_data(indicator, period)
                analysis = source.get_analysis(data, period)
                chart_info = await source.create_chart(data, indicator, period)
                
                period_name = {"6mo": "6 Months", "1y": "1 Year", "2y": "2 Years"}.get(period, period)
                
                output = f"""{period_name} Analysis ({indicator}):
                        - Latest ({analysis['latest_date']}): {analysis['latest']:.3f}"""
                
                if 'change_1w' in analysis:
                    output += f"\n- 1 Week Change: {analysis['change_1w']:+.3f}"
                if 'change_1m' in analysis:
                    output += f"\n- 1 Month Change: {analysis['change_1m']:+.3f}"
                
                output += f"\n\n{chart_info}"
                
                return output
            except Exception as e:
                return f"Error fetching FRED data for {indicator}: {str(e)}"
        
        return get_fred_data
    
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
        - This includes introductions, explanations, and all text output

        CRITICAL RULES:
        - NEVER try to create or output images directly in your text
        - ONLY use the provided tools to generate charts
        - DO NOT use markdown image syntax like ![image] in your responses
        - Charts will be automatically displayed by the system after you use the tools

        Available tools:
        1. get_yf_data(symbol, period): Get stock/treasury data from Yahoo Finance
           - Use for: stocks (AAPL, SPY), treasuries (^TNX, ^FVX), indices
        2. get_fred_data(indicator, period="6mo"): Get economic data from FRED
           - Use for: NFCI, DFF, T10Y2Y, UNRATE, etc.

        WORKFLOW:
        1. Analyze the requested ticker/indicator from user input
        2. Call appropriate tool for each period (5d, 1mo, 6mo)
        3. FORMAT OUTPUT AS MARKDOWN TABLE
        4. Include ALL chart links from tool responses
        
        OUTPUT FORMAT (REQUIRED):
        Start with a brief introduction.
        Then create a markdown table with ALL analysis results.
        
        | Period | Start | End | Change | High | Low | Volatility |
        |--------|-------|-----|--------|------|-----|------------|
        | 5 Days | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        | 1 Month | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        | 6 Months | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        
        Then add chart links and comprehensive insights.

        CRITICAL - CHART LINKS: 
        - You MUST include the EXACT "Chart saved: /path/to/file.png" messages from ALL tools
        - Copy the FULL file path EXACTLY as returned (do NOT modify or shorten the path)
        - Use the format: [View Chart](sandbox:/full/exact/path.png)
        - ALL chart links MUST appear in the final output

        {self.context_instructions}

        Today is {datetime.now().strftime("%Y-%m-%d")}.
        """
        
        return Agent(
            name=self.agent_name,
            instructions=instructions,
            model="gpt-4o-mini",
            tools=[self.yfinance_tool, self.fred_tool],
            model_settings=ModelSettings(tool_choice="required")
        )
        