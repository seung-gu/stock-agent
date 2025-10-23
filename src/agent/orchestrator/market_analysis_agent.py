from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from src.agent.orchestrator.liquidity_agent import LiquidityAgent
from src.agent.trend.equity_agent import EquityTrendAgent
from src.agent.base.orchestrator_agent import OrchestratorAgent
from pydantic import BaseModel, Field
import asyncio
import json
from typing import List

from src.config import REPORT_LANGUAGE
from src.adapters.report_builder import upload_report_with_children
from src.services.image_service import find_local_images, upload_images_to_cloudflare

load_dotenv(override=True)


class ReportData(BaseModel):
    """Market analysis report data structure."""
    title: str = Field(description="The title of the report")
    date: str = Field(description="The date of the report")
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    main_report: str = Field(description="Conclusion and insights in markdown format")
    child_page_titles: list[str] = Field(description="Titles for child pages")


instructions = f"""
You are a market strategist providing concluding insights by synthesizing liquidity and equity analyses.

LANGUAGE REQUIREMENT:
- ALL your responses MUST be in {REPORT_LANGUAGE}
- This includes title, summary, introduction, and all text output

You will receive two detailed analysis results:
1. Liquidity analysis from treasury yield trends (TNX, FVX, etc.)
2. Equity analysis from stock price trends (AAPL, SPY, TSLA, etc.)

IMPORTANT: These individual analyses are already complete. Your job is to provide CONCLUSION and STRATEGIC INSIGHTS.

YOUR TASK - Provide Conclusion & Insights:

1. KEY TAKEAWAYS:
   - What do these analyses together tell us?
   - What's the most important insight?
   - What should investors focus on?

2. MARKET STORY:
   - Rising yields + Rising stock = Strong fundamentals overcoming tightening liquidity
   - Falling yields + Rising stock = Ideal bullish environment (loosening liquidity boost)
   - Rising yields + Falling stock = Liquidity headwinds pressuring equities
   - Falling yields + Falling stock = Risk-off despite supportive liquidity (fundamental concerns)

3. INVESTMENT IMPLICATIONS:
   - What does this mean for investment decisions?
   - Key risks and opportunities
   - Time horizon considerations

4. ACTION ITEMS:
   - What should investors do (or not do)?
   - What to monitor
   - When to reassess

REPORT GENERATION:
- Write naturally and organically - you're writing the conclusion, not a detailed analysis
- Start with the biggest insight, then elaborate
- Be decisive and actionable
- Use markdown HEADINGS (# ## ###) for structure
- Keep it concise and impactful

OUTPUT REQUIRED:
- short_summary: 2-3 sentence summary in {REPORT_LANGUAGE}
- main_report: Full conclusion and insights in {REPORT_LANGUAGE}
- child_page_titles: List of page titles in {REPORT_LANGUAGE}

CRITICAL RULES:
- The input will contain chart links in format: [View Chart](sandbox:/path/to/file.png)
- DO NOT include chart links - charts are in individual analysis pages
- DO NOT repeat detailed data or statistics
- Focus ONLY on what it all means and what to do about it
- NEVER try to create or output images directly

Today is {datetime.now().strftime("%Y-%m-%d")}.
"""
        
# Market analysis agent (no tools, just analysis)
market_agent = Agent(
    name="market_analyzer",
    instructions=instructions,
    model="gpt-4.1-mini",
    output_type=ReportData
)


class MarketResearchManager(OrchestratorAgent):
    """
    Orchestrates the complete market research workflow:
    1. Run liquidity and equity analysis in parallel
    2. Generate conclusion and insights from the analyses
    3. Post structured report to Notion with child pages
    """
    
    def __init__(self, liquidity_ticker: str = "^TNX", equity_ticker: str = "AAPL"):
        """Initialize market research manager."""
        self.liquidity_ticker = liquidity_ticker
        self.equity_ticker = equity_ticker
        super().__init__("market_research_manager")
    
    def _setup(self):
        """Set up sub-agents and synthesis agent."""
        # Initialize and store sub-agents with references
        self.liquidity_agent = LiquidityAgent()
        self.equity_agent = EquityTrendAgent(self.equity_ticker)
        
        # Add to sub-agents list using method chaining
        self.add_sub_agent(self.liquidity_agent)\
            .add_sub_agent(self.equity_agent)
        
        # Create synthesis agent
        self.synthesis_agent = self._create_synthesis_agent(f"""
        You are a market strategist synthesizing multiple analysis results.

        LANGUAGE REQUIREMENT:
        - ALL your responses MUST be in {REPORT_LANGUAGE}

        YOUR TASK:
        - Combine the provided analysis results into comprehensive market insights
        - Identify key patterns and correlations between different analyses
        - Provide strategic insights and recommendations
        - Include ALL chart links from the original analyses
        - Maintain the unique characteristics of each analysis type
        """
        )
    
    async def run_full_analysis(self, equity_ticker: str, liquidity_ticker: str = "^TNX"):
        """
        Execute full market research workflow.
        
        Args:
            equity_ticker: Stock ticker to analyze (e.g., "AAPL", "SPY")
            liquidity_ticker: Treasury ticker for liquidity (default: "^TNX")
            
        Returns:
            Dictionary with page_id and url
        """
        with trace("market_research"):
            print(f"📊 Starting market research: {equity_ticker} + {liquidity_ticker}")
            
            # Step 1: Run individual analyses to get separate results
            print("📈 Running parallel analysis...")
            liquidity_result = await self.liquidity_agent.run()
            equity_result = await self.equity_agent.run(f"Analyze {equity_ticker} stock price trends for 5d, 1mo, 6mo periods")
            
            # Step 2: Generate report using market_agent
            print("🔍 Synthesizing insights and generating report...")
            report = await self._generate_report(
                equity_ticker, liquidity_ticker, liquidity_result, equity_result
            )
            
            # Step 3: Post to Notion
            print("📝 Posting to Notion...")
            result = await self._post_to_notion(
                report.model_dump_json(indent=4),
                liquidity_result, equity_result
            )
            
            print("✅ Market research complete!")
            return result
    
    
    async def _generate_report(
        self, 
        equity_ticker: str, 
        liquidity_ticker: str,
        liquidity_result: str,
        equity_result: str
    ) -> ReportData:
        """
        Generate conclusion and insights by synthesizing liquidity and equity analyses.
        Focus on strategic takeaways and actionable recommendations.
        """
        combined_input = f"""
        LIQUIDITY ANALYSIS ({liquidity_ticker}):
        {liquidity_result}
        
        EQUITY ANALYSIS ({equity_ticker}):
        {equity_result}
        
        Please provide comprehensive market insights and strategic recommendations.
        """
        
        result = await Runner.run(market_agent, input=combined_input)
        return result.final_output_as(ReportData)
    
    async def _post_to_notion(self, report_json: str, liquidity_result: str, equity_result: str) -> dict:
        """Post report to Notion with child pages."""
        report = json.loads(report_json)
        
        # Process all images once (for all pages)
        # Convert RunResult objects to strings if needed
        liquidity_str = liquidity_result.final_output if hasattr(liquidity_result, 'final_output') else str(liquidity_result)
        equity_str = equity_result.final_output if hasattr(equity_result, 'final_output') else str(equity_result)
        
        all_content = f"{report['main_report']}\n\n{liquidity_str}\n\n{equity_str}"
        _, image_files, _ = find_local_images(all_content)
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        
        # Prepare child pages
        child_pages = [
            (report['child_page_titles'][0], liquidity_str),
            (report['child_page_titles'][1], equity_str),
            (report['child_page_titles'][2], report['main_report'])
        ]
        
        # Upload report with children
        result = upload_report_with_children(
            title=report['title'],
            date=report['date'],
            summary=report['short_summary'],
            child_pages=child_pages,
            uploaded_map=uploaded_map
        )
        
        return result


# Usage examples
if __name__ == "__main__":
    async def main():
        # Create manager
        manager = MarketResearchManager()
        
        # Run complete workflow
        result = await manager.run_full_analysis(
            equity_ticker="AAPL",
            liquidity_ticker="^TNX"
        )
        
        print("\n" + "=" * 80)
        print("📊 FINAL REPORT")
        print("=" * 80)
        print(f"\n📄 Result: {result}")
        if isinstance(result, dict):
            print(f"📄 Page ID: {result.get('page_id', 'N/A')}")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
        else:
            print(f"📄 Result type: {type(result)}")
        
    asyncio.run(main())
