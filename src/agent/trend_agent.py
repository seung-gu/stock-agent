from datetime import datetime
from agents.result import T
from dotenv import load_dotenv
from agents import Agent, function_tool, ModelSettings
import yfinance as yf

from src.agent.async_agent import AsyncAgent
from src.utils.charts import create_single_chart

load_dotenv(override=True)


# Value Unit Determiner Agent Tool
get_value_unit = Agent(
    name="Unit Determiner",
    instructions="""
    Determine value unit for chart. Return ONE WORD ONLY.

    Rules (priority order):
    1. Name has "Treasury"/"Yield"/"CBOE Interest Rate" → PERCENTAGE
    2. Name has "S&P"/"NASDAQ"/"Dow" → INDEX
    3. Type is EQUITY → currency code (USD/EUR/JPY)
    4. Type is INDEX + value <100 → PERCENTAGE
    5. Type is INDEX + value >100 → INDEX
    6. Type is CURRENCY → RATE

    Examples:
    Apple Inc., EQUITY, USD → USD
    CBOE Interest Rate 10 Year, INDEX → PERCENTAGE
    S&P 500, INDEX → INDEX

    Return ONLY the unit word. No explanation.""",
    model="gpt-4o-mini"
).as_tool(
    tool_name="get_value_unit",
    tool_description="Determine chart value unit type"
)


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
        self.ticker_obj = yf.Ticker(self.ticker)
        self.analyze_trend_tool = self._create_analyze_tool()
        self.plot_trend_tool = self._create_plot_tool()
        
    
    def _create_analyze_tool(self):
        """Create analyze_trend tool with self captured via closure."""
        @function_tool
        def analyze_trend(period: str) -> str:
            """Analyze trend for specified period. Period options: 5d, 1mo, 6mo"""
            data = self.ticker_obj.history(period=period)
            
            if data.empty or len(data) < 2:
                return f"Insufficient data for {period}: {self.ticker}"
            
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100
            volatility = data['Close'].std()
            
            period_name = {"5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months"}.get(period, period)
            
            return f"""{period_name} Trend Analysis ({self.ticker}):
                    - Start: {start_price:.3f}
                    - End: {end_price:.3f}
                    - Change: {change_pct:+.2f}%
                    - High: {data['Close'].max():.3f}
                    - Low: {data['Close'].min():.3f}
                    - Volatility: {volatility:.3f}
                    - Data Points: {len(data)}"""
        
        return analyze_trend
    
    def _create_plot_tool(self):
        """Create plot_trend tool with self captured via closure."""
        @function_tool
        def plot_trend(period: str, value_type: str) -> str:
            """
            Plot trend chart for specified period.
            
            Args:
                period: Period options: 5d, 1mo, 6mo
                value_type: Value type returned from get_value_unit tool
                
            Note: Call get_value_unit tool first to determine value_type.
            """
            data = self.ticker_obj.history(period=period)
            
            # Determine ylabel and format based on value_type
            type_mapping = {
                "USD": ("Price ($)", "${:.2f}"),
                "EUR": ("Price (€)", "€{:.2f}"),
                "JPY": ("Price (¥)", "¥{:.2f}"),
                "GBP": ("Price (£)", "£{:.2f}"),
                "PERCENTAGE": ("Yield (%)", "{:.2f}%"),
                "INDEX": ("Index Value", "{:.2f}"),
                "RATE": ("Exchange Rate", "{:.4f}"),
            }
            
            # Default to currency code if not in mapping
            if value_type in type_mapping:
                ylabel, value_format = type_mapping[value_type]
            else:
                # Other currencies or unknown types
                ylabel = f"Price ({value_type})" if value_type else "Value"
                value_format = "{:.2f}"
            
            result = create_single_chart(self.ticker, data, period, ylabel, value_format)
            return result if result else f"Failed to generate {period} chart"
        
        return plot_trend
    
    def _create_agent(self) -> Agent:
        """
        Create the LLM agent with instructions and tools.
        
        Returns:
            Agent instance configured for trend analysis
        """
        instructions = f"""
        You are a specialized financial analyst for {self.ticker} trend analysis.

        CRITICAL RULES:
        - NEVER try to create or output images directly in your text
        - ONLY use the provided tools to generate charts
        - DO NOT use markdown image syntax like ![image] in your responses
        - Charts will be automatically displayed by the system after you use the tools

        Available tools:
        1. analyze_trend(period): Get trend analysis for any period (5d, 1mo, 6mo)
        2. get_value_unit(ticker_symbol, quote_type, currency, ticker_name, sample_value): 
           Returns unit type (USD/EUR/PERCENTAGE/INDEX/etc)
        3. plot_trend(period, value_type): Generate chart with unit type

        MANDATORY Workflow (YOU MUST FOLLOW EVERY STEP):
        1. analyze_trend("5d") - get metadata
        2. get_value_unit(...) - determine unit ONCE
        3. analyze_trend("5d") + plot_trend("5d", value_type) - MUST call plot
        4. analyze_trend("1mo") + plot_trend("1mo", value_type) - MUST call plot
        5. analyze_trend("6mo") + plot_trend("6mo", value_type) - MUST call plot
        6. **FORMAT OUTPUT AS MARKDOWN TABLE**
        
        YOU MUST CALL plot_trend() for EVERY period. Charts are REQUIRED, not optional.
        
        OUTPUT FORMAT (REQUIRED):
        Create a markdown table with ALL analysis results:
        
        | Period | Start | End | Change | High | Low | Volatility |
        |--------|-------|-----|--------|------|-----|------------|
        | 5 Days | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        | 1 Month | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        | 6 Months | X.XXX | X.XXX | -X.XX% | X.XXX | X.XXX | X.XXX |
        
        Then add chart links and comprehensive insights in Korean.

        CRITICAL: 
        - You MUST include the EXACT "Chart saved: /path/to/file.png" messages from plot_trend tools
        - Copy the FULL file path EXACTLY as returned (do NOT modify or shorten the path)
        - Use the format: [View Chart](sandbox:/full/exact/path.png)

        {self.context_instructions}

        Today is {datetime.now().strftime("%Y-%m-%d")}.
        """
        
        return Agent(
            name=self.agent_name,
            instructions=instructions,
            model="gpt-4o-mini",
            tools=[self.analyze_trend_tool, self.plot_trend_tool, get_value_unit],
            model_settings=ModelSettings(tool_choice="required")
        )
        