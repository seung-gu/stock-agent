"""Main entry point for market analysis"""

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from agents import trace

from src.services.image_service import find_local_images, upload_images_to_cloudflare
from src.agent.orchestrator.market_report_agent import MarketReportAgent
from src.adapters.report_builder import upload_report_with_children
from src.utils.data_sources import get_data_source

load_dotenv(override=True)


async def pre_fetch_common_data():
    """
    Pre-fetch common data before agent execution to improve cache hit rate.
    
    This fetches data for symbols that are used by multiple agents,
    reducing redundant API calls during agent execution.
    """
    print("🔄 Pre-fetching common data...")
    
    common_symbols = {
        'yfinance': ['^TNX', 'DX=F', '^GSPC', '^IXIC', '^DJI'],
        'fred': ['NFCI'],
        'investing': ['S5FI', 'S5TH']
    }
    
    tasks = []
    for source, symbols in common_symbols.items():
        src = get_data_source(source)
        for symbol in symbols:
            # Fetch longest period first (enables cache reuse for shorter periods)
            period = '5y' if source == 'yfinance' else '1y'
            tasks.append(src.fetch_data(symbol, period))
    
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
        print("✅ Common data pre-fetched")
    except Exception as e:
        print(f"⚠️ Warning: Some pre-fetch operations failed: {e}")
        # Continue execution even if pre-fetch fails


async def run_market_report():
    """
    Run complete market report workflow.
    """
    print(f"📊 Starting market report")
    
    with trace("run_market_report"):
        # Pre-fetch common data to improve cache hit rate
        await pre_fetch_common_data()
        
        market_report_agent = MarketReportAgent()
        final_report = await market_report_agent.run()
        
        report_contents = market_report_agent.sub_agent_results + [final_report]

        _, image_files, _ = find_local_images(" ".join([result.content for result in report_contents]))
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        
        child_pages = [(result.title, result.content) for result in report_contents]
  
        return upload_report_with_children(
            title=final_report.title,
            date=datetime.now().strftime('%Y-%m-%d'),
            summary=final_report.summary,
            child_pages=child_pages,
            uploaded_map=uploaded_map
        )



async def main():
    """Main entry point"""
    print("=" * 80)
    print("Market Report System")
    print("=" * 80)
    
    # Example 1: Complete market report
    print("\n📊 Running complete market report...")
    market_result = await run_market_report()
    print(f"Market Report Result: {market_result}")

if __name__ == "__main__":
    asyncio.run(main())
