from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, function_tool, ModelSettings

from src.agent.base.async_agent import AsyncAgent
from src.types.analysis_report import AnalysisReport
from src.utils.data_sources import get_data_source
from src.config import REPORT_LANGUAGE

load_dotenv(override=True)


class TrendAgent(AsyncAgent):
    """
    Trend analysis agent for trend analysis with reusable tools and agent creation.
    """
    
    def __init__(self, ticker: str, agent_name: str, context_instructions: str, tools: list = []):
        """
        Initialize trend analysis agent with ticker.
        
        Args:
            ticker: Ticker symbol (e.g., "^TNX", "AAPL")
            agent_name: Agent name identifier (e.g., "liquidity_agent_TNX")
            context_instructions: Specialized analysis instructions
            tools: List of tools to use (optional)
        """
        self.ticker = ticker
        self.context_instructions = context_instructions
        self.tools = tools
        self.output_type = AnalysisReport

        super().__init__(agent_name)
    
    @staticmethod
    def _get_period_name(period: str) -> str:
        """Get human-readable period name."""
        period_names = {
            "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
            "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
        }
        return period_names.get(period, f"{period}")
    
    @staticmethod
    async def _fetch_and_analyze(source_name: str, symbol: str, period: str, include_chart: bool = False) -> tuple[dict, dict, str]:
        """Common workflow for fetching, analyzing, and optionally charting data."""
        source = get_data_source(source_name)
        data = await source.fetch_data(symbol, period)
        analysis = source.get_analysis(data, period)
        chart_info = ""
        if include_chart:
            chart_info = await source.create_chart(data, symbol, period)
        return data, analysis, chart_info
    
    def _create_yfinance_tool(self):
        """Create yfinance data tool."""
        @function_tool
        async def get_yf_data(symbol: str, period: str, include_chart: bool = False) -> str:
            """
            Get stock, ETF, or treasury data from Yahoo Finance.
            
            Args:
                symbol: Ticker symbol (e.g., ^TNX, AAPL, SPY)
                period: Time period (5d, 1mo, 3mo, 6mo, 1y, 2y, 5y or 10y)
                
            Returns:
                Analysis with price data and chart link
            """
            try:
                data, analysis, chart_info = await TrendAgent._fetch_and_analyze("yfinance", symbol, period, include_chart)
                period_name = TrendAgent._get_period_name(period)
                
                sma_info = ""
                if analysis.get('sma'):
                    sma_info = f"\n                        - Moving Averages: {analysis['sma']}"
                
                output = f"""{period_name} Analysis ({symbol}):
                        - Start: {analysis['start']:.3f}
                        - End: {analysis['end']:.3f}
                        - Change: {analysis['change_pct']:+.2f}%
                        - High: {analysis['high']:.3f}
                        - Low: {analysis['low']:.3f}
                        - Volatility: {analysis['volatility']:.3f}{sma_info}
                        {chart_info}"""
                
                return output
            except Exception as e:
                return f"Error fetching data for {symbol}: {str(e)}"
        
        return get_yf_data
    
    def _create_fred_tool(self):
        """Create FRED economic data tool."""
        @function_tool
        async def get_fred_data(indicator: str, period: str = "6mo", include_chart: bool = False) -> str:
            """
            Get economic indicator data from FRED (Federal Reserve Economic Data).
            
            Args:
                indicator: FRED indicator code (e.g., NFCI, DFF, T10Y2Y, UNRATE)
                period: Time period (5d, 1mo, 3mo, 6mo, 1y, 2y, 5y or 10y)
                
            Returns:
                Analysis with indicator data and chart link
            """
            try:
                data, analysis, chart_info = await TrendAgent._fetch_and_analyze("fred", indicator, period, include_chart)
                period_name = TrendAgent._get_period_name(period)
                
                output = f"""{period_name} Analysis ({indicator}):
                        - Start: {analysis['start']:.3f}
                        - End: {analysis['end']:.3f}
                        - Change: {analysis['change_pct']:+.2f}%
                        - High: {analysis['high']:.3f}
                        - Low: {analysis['low']:.3f}
                        - Volatility: {analysis['volatility']:.3f}
                        {chart_info}"""
                
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

        CRITICAL RULES:
        - NEVER try to create or output images directly in your text
        - ONLY use the provided tools to generate charts
        - DO NOT use markdown image syntax like ![image] in your responses
        - Charts will be automatically displayed by the system after you use the tools

        WORKFLOW:
        1. Analyze the ticker: {self.ticker}
        2. Call appropriate tool for each period using {self.ticker}
        3. When calling the tools, always call the longest period first and then call the shorter periods in reverse order
        4. FORMAT OUTPUT AS MARKDOWN TABLE
        5. Include ALL chart links from tool responses in the order of the periods
        
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
        - title: Create a specific, descriptive title for {self.ticker} analysis
        - summary: Executive summary of key findings for {self.ticker}
        - content: The detailed analysis content above for {self.ticker}

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
        