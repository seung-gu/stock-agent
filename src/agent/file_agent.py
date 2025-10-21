import os
from datetime import datetime
from typing import Dict
from agents import Agent, function_tool


@function_tool
def save_report(title: str, content: str) -> Dict[str, str]:
    """
    리포트를 마크다운 파일로 저장.
    
    Args:
        title: 리포트 제목
        content: 리포트 내용
        
    Returns:
        저장된 파일 경로
    """
    try:
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"market_report_{timestamp}.md"
        filepath = f"/tmp/{filename}"
        
        # 마크다운 파일 생성
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(content)
        
        print(f"✅ 리포트 저장 완료: {filepath}")
        return {"status": "success", "filepath": filepath}
        
    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return {"status": "error", "message": str(e)}


INSTRUCTIONS = """간단한 파일 저장 에이전트입니다.

받은 리포트를 마크다운 파일로 저장합니다.
- 제목과 내용을 정리해서 파일로 저장
- 복잡한 API 없이 단순하게 처리"""

file_agent = Agent(
    name="File Agent",
    instructions=INSTRUCTIONS,
    tools=[save_report],
    model="gpt-4o-mini",
)
