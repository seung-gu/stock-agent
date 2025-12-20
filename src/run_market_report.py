"""Main entry point for market analysis"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from agents import trace, set_default_openai_client
from openai import AsyncOpenAI

from src.agent.orchestrator.market_report_agent import MarketReportAgent
from src.adapters.notion_report_builder import NotionReportBuilder

load_dotenv(override=True)

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx._client").setLevel(logging.WARNING)
logging.getLogger("httpx.client").setLevel(logging.WARNING)


async def run_market_report():
    """Run complete market report workflow."""
    print(f"📊 Starting market report")
    
    with trace("run_market_report"):
        # Execute analysis
        market_report_agent = MarketReportAgent()
        final_report = await market_report_agent.run()
        
        # Extract individual results and agents
        liquidity_result = market_report_agent.sub_agent_results[0]
        health_result = market_report_agent.sub_agent_results[1]
        index_result = market_report_agent.sub_agent_results[2]
        portfolio_result = market_report_agent.sub_agent_results[3]
        portfolio_agent = market_report_agent.sub_agents[3]
        
        # Build hierarchical report structure
        builder = NotionReportBuilder()
        builder.add_page(liquidity_result)\
            .add_page(health_result)\
            .add_page(index_result)\
            .add_page(portfolio_result)\
                .add_children(portfolio_agent.sub_agent_results)\
            .add_page(final_report)
        
        # Upload to Notion (images are automatically processed)
        return builder.upload(
            title=final_report.title,
            date=datetime.now().strftime('%Y-%m-%d'),
            summary=final_report.summary
        )


async def main():
    """Main entry point"""
    # Set OpenAI client with extended timeout (20 minutes)
    # Default timeout is 10 minutes (600 seconds), increasing to 20 minutes (1200 seconds)
    client = AsyncOpenAI(timeout=1200.0)
    set_default_openai_client(client)
    print("⏱️  OpenAI API timeout set to 20 minutes (1200 seconds)")
    
    print("=" * 80)
    print("Market Report System")
    print("=" * 80)
    
    # Example 1: Complete market report
    print("\n📊 Running complete market report...")
    market_result = await run_market_report()
    print(f"Market Report Result: {market_result}")

if __name__ == "__main__":
    asyncio.run(main())
