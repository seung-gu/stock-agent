from datetime import datetime
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from liquidity_agent import LiquidityTrendAgent
from equity_agent import EquityTrendAgent
from notion_agent import notion_agent
from pydantic import BaseModel, Field
import asyncio

load_dotenv(override=True)


class ReportData(BaseModel):
    """Market analysis report data structure."""
    short_summary: str = Field(description="A short 2-3 sentence summary of the findings.")
    markdown_report: str = Field(description="The final report in markdown format")
    follow_up_questions: list[str] = Field(description="Suggested topics to research further")


instructions = f"""
You are a comprehensive market analyst providing integrated analysis by examining both liquidity conditions and equity trends.

You will receive two analysis results:
1. Liquidity analysis from treasury yield trends (TNX, FVX, etc.)
2. Equity analysis from stock price trends (AAPL, SPY, TSLA, etc.)

YOUR TASK:

1. CORRELATION ANALYSIS:
   - Compare liquidity trends with equity performance
   - Identify alignment or divergence between the two
   - Assess if equity movements are supported by liquidity conditions

2. INTEGRATED INSIGHTS:
   - Rising yields + Rising stock = Strong fundamentals overcoming tightening liquidity
   - Falling yields + Rising stock = Ideal bullish environment (loosening liquidity boost)
   - Rising yields + Falling stock = Liquidity headwinds pressuring equities
   - Falling yields + Falling stock = Risk-off despite supportive liquidity (fundamental concerns)

3. TIMEFRAME-SPECIFIC ANALYSIS:
   - Short-term (5 days): Immediate momentum and trend alignment
   - Medium-term (1 month): Trend confirmation and divergences
   - Long-term (6 months): Structural trends and strategic positioning

4. ACTIONABLE RECOMMENDATIONS:
   - Investment outlook based on integrated analysis
   - Key risks from liquidity or equity side
   - Monitoring points and potential catalysts
   - Entry/exit timing considerations

KEY ANALYSIS POINTS:
- How liquidity conditions support or hinder equity performance
- Whether current equity valuation is justified given liquidity backdrop
- Divergences between liquidity and equity trends (opportunities or warnings)
- Risk appetite indicators from both markets
- Integer percentage level crossings and their significance

REPORT GENERATION:
- First create an outline for the report describing structure and flow
- Then generate the full report in markdown format
- The report should be lengthy and detailed (5-10 pages, at least 1000 words)
- Include executive summary, detailed analysis, and actionable recommendations

CHART INTEGRATION - VERY IMPORTANT:
- The input will contain chart links in format: [차트 보기](sandbox:/path/to/file.png)
- You MUST preserve these EXACT markdown links in your report
- Place charts immediately after their corresponding analysis sections
- Example structure:
  ## 단기 분석 (5일)
  분석 내용...
  [5일 차트 보기](sandbox:/path/to/TNX_5_days_chart.png)
  
  ## 중기 분석 (1개월)
  분석 내용...
  [1개월 차트 보기](sandbox:/path/to/TNX_1_month_chart.png)

CRITICAL RULES:
- NEVER try to create or output images directly
- PRESERVE the exact markdown image links from the input (do NOT change the format)
- Place charts right after their analysis sections, NOT at the end
- Output must follow ReportData schema (short_summary, markdown_report, follow_up_questions)

Today is {datetime.now().strftime("%Y-%m-%d")}.
Always explain in Korean and provide comprehensive, actionable market insights.
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
    2. Synthesize integrated market insights and generate report
    3. Send report via email
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
            
            # Step 3: Post to Notion
            print("📝 Posting to Notion...")
            # 차트 파일 경로 정보도 함께 전달
            combined_content = f"""
            === 유동성 분석 ===
            {liquidity_result}

            === 주식 분석 ===
            {equity_result}

            === 종합 리포트 ===
            {report.markdown_report}

            === 차트 파일 정보 ===
            차트 파일들이 임시 디렉토리에 저장되었습니다.
            """
            await self._post_to_notion(combined_content)
            
            print("✅ Market research complete!")
            return report
    
    async def _run_parallel_analysis(self, equity_ticker: str, liquidity_ticker: str):
        """Run liquidity and equity analysis in parallel."""
        liquidity_agent = LiquidityTrendAgent(liquidity_ticker)
        equity_agent = EquityTrendAgent(equity_ticker)
        
        results = await asyncio.gather(
            liquidity_agent.run(f"{liquidity_ticker}의 5일, 1개월, 6개월 추세를 분석하고 차트도 보여줘"),
            equity_agent.run(f"{equity_ticker}의 5일, 1개월, 6개월 추세를 분석하고 차트도 보여줘")
        )
        
        return results[0].final_output, results[1].final_output
    
    async def _generate_report(
        self, 
        equity_ticker: str, 
        liquidity_ticker: str,
        liquidity_output: str,
        equity_output: str
    ) -> ReportData:
        """
        Generate comprehensive market report directly from market_agent.
        market_agent now outputs ReportData directly (no need for writer_agent).
        """
        combined_input = f"""
Original Query: {equity_ticker} 시장 분석 (유동성 조건 포함)

=== Liquidity Analysis ({liquidity_ticker}) ===
{liquidity_output}

=== Equity Analysis ({equity_ticker}) ===
{equity_output}

위 두 분석을 종합하여 {equity_ticker} 투자에 대한 상세한 리포트를 작성해주세요.
리포트는 전문적이고 구조화된 마크다운 형식이어야 합니다.
"""
        
        result = await Runner.run(market_agent, input=combined_input)
        return result.final_output_as(ReportData)
    
    async def _post_to_notion(self, report: str) -> None:
        """Post report to Notion using notion_agent."""
        await Runner.run(notion_agent, input=report)
        print("📝 Notion 자동 업로드 완료!")


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
        print(f"\n📄 Full Report:\n{report.markdown_report}")
        print(f"\n🔍 Follow-up Questions: {report.follow_up_questions}")
        
    asyncio.run(main())
