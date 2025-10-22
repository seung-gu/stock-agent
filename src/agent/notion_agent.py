from typing import Dict
from agents import Agent, ModelSettings, function_tool
from dotenv import load_dotenv

from src.services.image_service import find_local_images, upload_images_to_cloudflare
from src.adapters.notion_api import upload_to_notion

load_dotenv(override=True)


@function_tool
def post_to_notion(title: str, content: str) -> Dict[str, str]:
    """Notion에 자동 포스트"""
    try:
        processed_content, image_files, image_map = find_local_images(content)
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        return upload_to_notion(title, processed_content, uploaded_map)
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {"status": "error", "message": str(e)}


INSTRUCTIONS = """Notion 자동 업로드 에이전트입니다.

받은 리포트를 Notion에 자동으로 업로드합니다.
- 제목과 내용을 정리해서 Notion 페이지로 생성
- API를 통해 자동으로 업로드
- 수동 작업 없이 완전 자동화"""

notion_agent = Agent(
    name="Notion Agent",
    instructions=INSTRUCTIONS,
    tools=[post_to_notion],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required")
)
