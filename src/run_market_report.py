"""Main entry point for market analysis"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
from agents import trace

from src.services.image_service import find_local_images, upload_images_to_cloudflare
from src.agent.orchestrator.market_report_agent import MarketReportAgent
from src.adapters.report_builder import upload_report_with_children

load_dotenv(override=True)

# Suppress httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpx._client").setLevel(logging.WARNING)
logging.getLogger("httpx.client").setLevel(logging.WARNING)


async def run_market_report():
    """
    Run complete market report workflow.
    """
    print(f"📊 Starting market report")
    
    with trace("run_market_report"):
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
