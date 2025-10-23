from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from liquidity_agent import LiquidityTrendAgent
from equity_agent import EquityTrendAgent
from pydantic import BaseModel, Field
import asyncio
import json

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


class MarketResearchManager:
    """
    Orchestrates the complete market research workflow:
    1. Run liquidity and equity analysis in parallel
    2. Generate conclusion and insights from the analyses
    3. Post structured report to Notion with child pages
    """
    
    async def run(self, equity_ticker: str, liquidity_ticker: str = "^TNX"):
        """
        Execute full market research workflow.
        
        Args:
            equity_ticker: Stock ticker to analyze (e.g., "AAPL", "SPY")
            liquidity_ticker: Treasury ticker for liquidity (default: "^TNX")
            
        Returns:
            ReportData with markdown report and metadata
        """
        with trace("market_research"):
            print(f"📊 Starting market research: {equity_ticker} + {liquidity_ticker}")
            
            # Step 1: Parallel analysis
            print("📈 Running parallel analysis...")
            liquidity_result, equity_result = await self._run_parallel_analysis(
                equity_ticker, liquidity_ticker
            )
            
            # Step 2: Integrated analysis & report generation (market_agent now outputs ReportData)
            print("🔍 Synthesizing insights and generating report...")
            report = await self._generate_report(
                equity_ticker, liquidity_ticker, liquidity_result, equity_result
            )
            
            # Step 3: Post to Notion (pass original analysis results, not market_agent's version)
            print("📝 Posting to Notion...")
            await self._post_to_notion(
                report.model_dump_json(indent=4),
                liquidity_result,  # original liquidity analysis result
                equity_result       # original equity analysis result
            )
            
            print("✅ Market research complete!")
            return report
    
    async def _run_parallel_analysis(self, equity_ticker: str, liquidity_ticker: str):
        """Run liquidity and equity analysis in parallel."""
        liquidity_agent = LiquidityTrendAgent(liquidity_ticker)
        equity_agent = EquityTrendAgent(equity_ticker)
        
        results = await asyncio.gather(
            liquidity_agent.run(
                f"{liquidity_ticker} 5d, 1mo, 6mo trend analysis and show charts. Consider that this is a 10-years interest rate for liquidity trend analysis."),
            equity_agent.run(f"{equity_ticker} 5d, 1mo, 6mo trend analysis and show charts")
        )
        
        return [result.final_output for result in results]
    
    async def _generate_report(
        self, 
        equity_ticker: str, 
        liquidity_ticker: str,
        liquidity_output: str,
        equity_output: str
    ) -> ReportData:
        """
        Generate conclusion and insights by synthesizing liquidity and equity analyses.
        Focus on strategic takeaways and actionable recommendations.
        """
        combined_input = f"""
        LIQUIDITY ANALYSIS ({liquidity_ticker}):
        {liquidity_output}
        
        EQUITY ANALYSIS ({equity_ticker}):
        {equity_output}
        """
        
        result = await Runner.run(market_agent, input=combined_input)
        return result.final_output_as(ReportData)
    
    async def _post_to_notion(self, report_json: str, original_liquidity: str, original_equity: str) -> None:
        """Post report to Notion with child pages."""
        report = json.loads(report_json)
        
        # Process all images once (for all pages)
        all_content = f"{report['main_report']}\n\n{original_liquidity}\n\n{original_equity}"
        _, image_files, _ = find_local_images(all_content)
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        
        # Prepare child pages
        child_pages = [
            (report['child_page_titles'][0], original_liquidity),
            (report['child_page_titles'][1], original_equity),
            (report['child_page_titles'][2], report['main_report'])
        ]
        
        # Upload report with children
        upload_report_with_children(
            title=report['title'],
            date=report['date'],
            summary=report['short_summary'],
            child_pages=child_pages,
            uploaded_map=uploaded_map
        )


# Usage examples
if __name__ == "__main__":
    async def main():
        # Create manager
        manager = MarketResearchManager()
        
        # Run complete workflow
        report = await manager.run(
            equity_ticker="AAPL",
            liquidity_ticker="^TNX"
        )
        
        print("\n" + "=" * 80)
        print("📊 FINAL REPORT")
        print("=" * 80)
        print(f"\n📋 Summary: {report.short_summary}")
        print(f"\n📄 Full Report:\n{report.main_report}")
        
    asyncio.run(main())
