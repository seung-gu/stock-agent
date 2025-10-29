from datetime import datetime
from agents.result import T
from dotenv import load_dotenv
from agents import Agent, function_tool, ModelSettings

from src.agent.base.async_agent import AsyncAgent
from src.types.analysis_report import AnalysisReport
from src.utils.data_sources import get_data_source
import pandas as pd
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
    
    def _create_yfinance_tool(self):
        """Create yfinance data tool."""
        @function_tool
        async def get_yf_data(symbol: str, period: str) -> str:
            """
            Get stock, ETF, or treasury data from Yahoo Finance.
            
            Args:
                symbol: Ticker symbol (e.g., ^TNX, AAPL, SPY)
                period: Time period (5d, 1mo, 3mo, 6mo, 1y, 2y, 5y or 10y)
                
            Returns:
                Analysis with price data and chart link
            """
            try:
                source = get_data_source("yfinance")
                data = await source.fetch_data(symbol, period)
                analysis = source.get_analysis(data, period)
                chart_info = await source.create_chart(data, symbol, period)
                
                period_name = {
                    "5d": "5 Days", "1mo": "1 Month", "3mo": "3 Months", "6mo": "6 Months",
                    "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
                }.get(period, f"{period} (default: 6mo)")
                
                # Extract SMA info if available
                hist = data.get('history')
                sma_info = ""
                if hist is not None and not hist.empty:
                    latest = hist.iloc[-1]
                    sma_parts = []
                    if 'SMA_5' in hist.columns and not pd.isna(latest.get('SMA_5')):
                        sma_parts.append(f"SMA(5): {latest['SMA_5']:.3f}")
                    if 'SMA_20' in hist.columns and not pd.isna(latest.get('SMA_20')):
                        sma_parts.append(f"SMA(20): {latest['SMA_20']:.3f}")
                    if 'SMA_200' in hist.columns and not pd.isna(latest.get('SMA_200')):
                        sma_parts.append(f"SMA(200): {latest['SMA_200']:.3f}")
                    if sma_parts:
                        sma_info = f"\n                        - Moving Averages: {', '.join(sma_parts)}"
                
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
        async def get_fred_data(indicator: str, period: str = "6mo") -> str:
            """
            Get economic indicator data from FRED (Federal Reserve Economic Data).
            
            Args:
                indicator: FRED indicator code (e.g., NFCI, DFF, T10Y2Y, UNRATE)
                period: Time period (5d, 1mo, 3mo, 6mo, 1y, 2y, 5y or 10y)
                
            Returns:
                Analysis with indicator data and chart link
            """
            try:
                source = get_data_source("fred")
                data = await source.fetch_data(indicator, period)
                analysis = source.get_analysis(data, period)
                chart_info = await source.create_chart(data, indicator, period)
                
                period_name = {
                    "6mo": "6 Months", "1y": "1 Year", "2y": "2 Years", "5y": "5 Years", "10y": "10 Years"
                }.get(period, f"{period} (default: 6mo)")
                
                output = f"""{period_name} Analysis ({indicator}):
                        - Start: {analysis['start']:.3f}
                        - End: {analysis['end']:.3f}
                        - Change: {analysis['change_pct']:+.2f}%
                        - High: {analysis['high']:.3f}
                        - Low: {analysis['low']:.3f}
                        - Volatility: {analysis['volatility']:.3f}"""
                
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

        CRITICAL RULES:
        - NEVER try to create or output images directly in your text
        - ONLY use the provided tools to generate charts
        - DO NOT use markdown image syntax like ![image] in your responses
        - Charts will be automatically displayed by the system after you use the tools

        WORKFLOW:
        1. Analyze the ticker: {self.ticker}
        2. Call appropriate tool for each period using {self.ticker}
        3. FORMAT OUTPUT AS MARKDOWN TABLE
        4. Include ALL chart links from tool responses
        
        OUTPUT FORMAT (REQUIRED):
        Start with a brief introduction.
        Then create a markdown table with analysis results for the requested periods.
        
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
        