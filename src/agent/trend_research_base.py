from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, ModelSettings
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile
import os

load_dotenv(override=True)

# Create temp directory for charts
TEMP_CHART_DIR = tempfile.mkdtemp(prefix="market_charts_")


# Value Unit Determiner Agent
_value_unit_agent = Agent(
    name="Unit Determiner",
    instructions="""Determine value unit for chart. Return ONE WORD ONLY.

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
)

# Convert Agent to tool
get_value_unit = _value_unit_agent.as_tool(
    tool_name="get_value_unit",
    tool_description="Determine chart value unit type"
)


def create_single_chart(ticker: str, data, period_name: str, color: str, ylabel: str, value_format: str) -> str:
    """
    Create a single trend chart for the given ticker and period.
    
    Args:
        ticker: Ticker symbol (e.g., "^TNX")
        data: Historical price data from yfinance
        period_name: Display name for the period (e.g., "5 Days")
        color: Chart color in hex format
        ylabel: Y-axis label (e.g., "Price ($)", "Yield (%)")
        value_format: Format string for values (e.g., "${:.2f}", "{:.2f}%")
        
    Returns:
        Filename of the saved chart or None if data is empty
    """
    if data.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], linewidth=2, color=color, marker='o', markersize=4)
    ax.fill_between(data.index, data['Close'], alpha=0.3, color=color)
    ax.set_title(f'{ticker} {period_name} Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Display start/end values
    start_val = data['Close'].iloc[0]
    end_val = data['Close'].iloc[-1]
    change = ((end_val - start_val) / start_val) * 100
    
    change_color = 'green' if change < 0 else 'red'
    ax.text(0.02, 0.95, f'Start: {value_format.format(start_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.85, f'End: {value_format.format(end_val)}', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.75, f'Change: {change:+.2f}%', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor=change_color, alpha=0.3))
    
    # Set Y-axis limits dynamically based on data range
    y_min = float(data['Close'].min())
    y_max = float(data['Close'].max())
    span = y_max - y_min
    padding = max(abs(y_min) * 0.01, 0.05) if span == 0 else span * 0.10
    ax.set_ylim(y_min - padding, y_max + padding)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    
    # Save chart to temp directory
    ticker_clean = ticker.replace('^', '').replace('-', '_')
    filename = f"{ticker_clean}_{period_name.lower().replace(' ', '_')}_chart.png"
    filepath = os.path.join(TEMP_CHART_DIR, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close()
    
    return f"Chart saved: {filepath}\n\nIMPORTANT: Copy this EXACT path to create markdown link: [View Chart](sandbox:{filepath})"


class TrendResearchBase:
    """
    Base class for trend analysis with reusable tools and agent creation.
    
    Provides:
    - Ticker data caching
    - Tool creation (analyze_trend, plot_trend)
    - Common agent creation workflow
    
    Subclasses only need to pass context_instructions in __init__.
    """
    
    def __init__(self, ticker: str, agent_name: str, context_instructions: str):
        """
        Initialize base trend research with ticker.
        
        Args:
            ticker: Ticker symbol (e.g., "^TNX", "AAPL")
            agent_name: Agent name identifier (e.g., "liquidity_agent_TNX")
            context_instructions: Specialized analysis instructions
        """
        self.ticker = ticker
        self.agent_name = agent_name
        self.context_instructions = context_instructions
        self._ticker_obj = None  # Cache for yfinance Ticker object
        
        # Create shared tools
        self.analyze_trend_tool = self._create_analyze_tool()
        self.plot_trend_tool = self._create_plot_tool()
        
        # Create specialized agent
        self.agent = self._create_agent()
        
    def get_ticker(self) -> yf.Ticker:
        """
        Get cached yfinance Ticker object (lazy initialization).
        
        Returns:
            yfinance Ticker object for this instance's ticker symbol
        """
        if self._ticker_obj is None:
            self._ticker_obj = yf.Ticker(self.ticker)
        return self._ticker_obj
    
    def _create_analyze_tool(self):
        """
        Create analyze_trend tool with self captured via closure.
        
        Returns:
            function_tool decorated function that analyzes trends
        """
        @function_tool
        def analyze_trend(period: str) -> str:
            """Analyze trend for specified period. Period options: 5d, 1mo, 6mo"""
            ticker_obj = self.get_ticker()
            data = ticker_obj.history(period=period)
            
            if data.empty or len(data) < 2:
                return f"Insufficient data for {period}: {self.ticker}"
            
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            change_pct = ((end_price - start_price) / start_price) * 100
            volatility = data['Close'].std()
            
            period_name = {"5d": "5-Day", "1mo": "1-Month", "6mo": "6-Month"}.get(period, period)
            
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
        """
        Create plot_trend tool with self captured via closure.
        
        Returns:
            function_tool decorated function that creates charts
        """
        @function_tool
        def plot_trend(period: str, value_type: str) -> str:
            """
            Plot trend chart for specified period.
            
            Args:
                period: Period options: 5d, 1mo, 6mo
                value_type: 값 타입 (get_chart_value_type tool에서 반환된 값)
                    - "USD" → Y-axis: "Price ($)", format: "${:.2f}"
                    - "EUR" → Y-axis: "Price (€)", format: "€{:.2f}"
                    - "JPY" → Y-axis: "Price (¥)", format: "¥{:.2f}"
                    - "PERCENTAGE" → Y-axis: "Yield (%)", format: "{:.2f}%"
                    - "INDEX" → Y-axis: "Index Value", format: "{:.2f}"
                    - "RATE" → Y-axis: "Exchange Rate", format: "{:.4f}"
                
            Note: 먼저 get_chart_value_type tool을 사용해 value_type을 결정하세요.
            """
            ticker_obj = self.get_ticker()
            data = ticker_obj.history(period=period)
            
            # value_type에 따라 ylabel과 format 결정
            type_mapping = {
                "USD": ("Price ($)", "${:.2f}"),
                "EUR": ("Price (€)", "€{:.2f}"),
                "JPY": ("Price (¥)", "¥{:.2f}"),
                "GBP": ("Price (£)", "£{:.2f}"),
                "PERCENTAGE": ("Yield (%)", "{:.2f}%"),
                "INDEX": ("Index Value", "{:.2f}"),
                "RATE": ("Exchange Rate", "{:.4f}"),
            }
            
            # 매핑에 없는 타입이면 통화코드로 간주
            if value_type in type_mapping:
                ylabel, value_format = type_mapping[value_type]
            else:
                # 기타 통화나 알 수 없는 타입
                ylabel = f"Price ({value_type})" if value_type else "Value"
                value_format = "{:.2f}"
            
            period_name = {"5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months"}.get(period, period)
            colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c"}
            color = colors.get(period, "#1f77b4")
            
            result = create_single_chart(self.ticker, data, period_name, color, ylabel, value_format)
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
        - Use the format: [차트 보기](sandbox:/full/exact/path.png)

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
    
    async def run(self, message: str):
        """
        Execute the agent with a user message.
        
        Args:
            message: User's analysis request
            
        Returns:
            Agent's response with analysis results
        """
        result = await Runner.run(self.agent, input=message)
        return result
