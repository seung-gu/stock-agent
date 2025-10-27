"""Main entry point for market analysis"""

import asyncio
from datetime import datetime
from dotenv import load_dotenv
from agents import trace

load_dotenv(override=True)


async def run_market_report():
    """
    Run complete market report workflow.
    """
    print(f"📊 Starting market report")
    
    with trace("run_market_report"):
        # 2. Notion 구조 생성
        from src.agent.notion_template_agent import NotionTemplateAgent
        from src.agent.orchestrator.market_report_agent import MarketReportAgent
        
        orchestrator = MarketReportAgent()
        notion_agent = NotionTemplateAgent()
        
        sub_agent_names = [agent.__class__.__name__ for agent in orchestrator.sub_agents]
        structure = await notion_agent.generate_template(sub_agent_names + ["Market Strategy Summary"])
        
        # 1. 분석 실행
        sub_agent_results = await orchestrator.run_sub_agents()
        synthesis_result = await orchestrator.run_synthesis(sub_agent_results)

        # 3. 이미지 처리
        from src.services.image_service import find_local_images, upload_images_to_cloudflare
        
        all_content = "\n\n".join([
            synthesis_result,
            *[result.final_output if hasattr(result, 'final_output') else str(result) for result in sub_agent_results]
        ])
        _, image_files, _ = find_local_images(all_content)
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        
        # 4. Child pages 준비
        get_content = lambda result: result.final_output if hasattr(result, 'final_output') else str(result)
        all_results = [get_content(result) for result in sub_agent_results] + [synthesis_result]
        
        child_pages = [(page.title, content) for page, content in zip(structure.child_pages, all_results)]
        
        # 5. Notion 업로드
        from src.adapters.report_builder import upload_report_with_children
        
        return upload_report_with_children(
            title=structure.title,
            date=datetime.now().strftime('%Y-%m-%d'),
            summary=structure.summary,
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
