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


def create_single_chart(ticker: str, data, period_name: str, color: str) -> str:
    """
    Create a single trend chart for the given ticker and period.
    
    Args:
        ticker: Ticker symbol (e.g., "^TNX")
        data: Historical price data from yfinance
        period_name: Display name for the period (e.g., "5 Days")
        color: Chart color in hex format
        
    Returns:
        Filename of the saved chart or None if data is empty
    """
    if data.empty:
        return None
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(data.index, data['Close'], linewidth=2, color=color, marker='o', markersize=4)
    ax.fill_between(data.index, data['Close'], alpha=0.3, color=color)
    ax.set_title(f'{ticker} {period_name} Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel('Yield (%)', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Display start/end values
    start_val = data['Close'].iloc[0]
    end_val = data['Close'].iloc[-1]
    change = ((end_val - start_val) / start_val) * 100
    
    change_color = 'green' if change < 0 else 'red'
    ax.text(0.02, 0.95, f'Start: {start_val:.2f}%', transform=ax.transAxes, 
            verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.text(0.02, 0.85, f'End: {end_val:.2f}%', transform=ax.transAxes, 
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
    
    return f"Chart saved: {filepath}"


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
                    - Start: {start_price:.3f}%
                    - End: {end_price:.3f}%
                    - Change: {change_pct:+.2f}%
                    - High: {data['Close'].max():.3f}%
                    - Low: {data['Close'].min():.3f}%
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
        def plot_trend(period: str) -> str:
            """Plot trend chart for specified period. Period options: 5d, 1mo, 6mo"""
            ticker_obj = self.get_ticker()
            data = ticker_obj.history(period=period)
            
            period_name = {"5d": "5 Days", "1mo": "1 Month", "6mo": "6 Months"}.get(period, period)
            colors = {"5d": "#1f77b4", "1mo": "#ff7f0e", "6mo": "#2ca02c"}
            color = colors.get(period, "#1f77b4")
            
            result = create_single_chart(self.ticker, data, period_name, color)
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
        2. plot_trend(period): Generate chart for any period (5d, 1mo, 6mo)

        Workflow:
        1. Use analyze_trend(period="5d") to get short-term analysis
        2. Use plot_trend(period="5d") to show short-term chart 
        3. Use analyze_trend(period="1mo") to get medium-term analysis
        4. Use plot_trend(period="1mo") to show medium-term chart
        5. Use analyze_trend(period="6mo") to get long-term analysis
        6. Use plot_trend(period="6mo") to show long-term chart
        7. Synthesize all analyses and provide comprehensive insights
        8. Always explain in Korean

        CRITICAL: You MUST include the exact "Chart saved: /path/to/file.png" messages from plot_trend tools in your final response.
        These file paths are needed for downstream processing (email reports with embedded images).

        {self.context_instructions}

        Today is {datetime.now().strftime("%Y-%m-%d")}. 
        Always explain in Korean and provide comprehensive analytical insights for {self.ticker}.
        """
        
        return Agent(
            name=self.agent_name,
            instructions=instructions,
            model="gpt-4o-mini",
            tools=[self.analyze_trend_tool, self.plot_trend_tool],
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
