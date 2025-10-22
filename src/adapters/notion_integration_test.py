#!/usr/bin/env python3
"""Notion Agent 통합 테스트 및 E2E 테스트"""

import asyncio
import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from agents import Runner
from src.agent.notion_agent import notion_agent
from src.adapters.notion_api import upload_to_notion

# 환경변수 로드
load_dotenv()


async def test_notion_basic():
    """기본 Notion 업로드 통합 테스트"""
    
    test_title = "기본 테스트 리포트"
    test_content = """
# 기본 테스트 리포트

이것은 Notion API 기본 테스트입니다.

## 주요 내용
- 항목 1
- 항목 2
- 항목 3

기본 테스트 완료!
"""
    
    print("=" * 80)
    print("🧪 기본 Notion Agent 테스트 시작...")
    print("=" * 80)
    
    result = await Runner.run(
        notion_agent,
        input=f"다음 내용을 Notion에 업로드해줘:\n\n제목: {test_title}\n\n내용:\n{test_content}"
    )
    
    print("\n" + "=" * 80)
    print("✅ 기본 테스트 완료!")
    print("=" * 80)
    if hasattr(result, 'final_output'):
        print(f"\n결과:\n{result.final_output}")
    else:
        print(f"\n결과:\n{result}")


async def test_notion_with_images():
    """이미지 포함 Notion 업로드 통합 테스트"""
    
    test_title = "이미지 테스트 리포트"
    test_content = """
# 이미지 테스트

이것은 Notion 이미지 업로드 테스트입니다.

## 차트 이미지들이 아래에 표시되어야 합니다:

![TNX 5일 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_5_days_chart.png)
![TNX 1개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_1_month_chart.png)
![TNX 6개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_6_months_chart.png)

이미지 테스트 완료!
"""
    
    print("=" * 80)
    print("🧪 이미지 포함 Notion Agent 테스트 시작...")
    print("=" * 80)
    
    result = await Runner.run(
        notion_agent,
        input=f"다음 내용을 Notion에 업로드해줘:\n\n제목: {test_title}\n\n내용:\n{test_content}"
    )
    
    print("\n" + "=" * 80)
    print("✅ 이미지 테스트 완료!")
    print("=" * 80)
    if hasattr(result, 'final_output'):
        print(f"\n결과:\n{result.final_output}")
    else:
        print(f"\n결과:\n{result}")


class TestNotionIntegration(unittest.TestCase):
    """Notion Agent 통합 테스트"""
    
    @patch('requests.post')
    @patch('boto3.client')
    @patch('PIL.Image.open')
    def test_full_workflow_with_mocks(self, mock_image_open, mock_boto3, mock_post):
        """전체 워크플로우 통합 테스트 (Mock 사용)"""
        # Mock 설정
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {'results': []}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 200
        mock_create_response.json.return_value = {
            'id': 'test-page-id',
            'url': 'https://notion.so/test'
        }
        
        mock_post.side_effect = [mock_search_response, mock_create_response]
        
        # 테스트 실행
        uploaded_map = {"/tmp/test.png": "https://example.com/image.jpg"}
        result = upload_to_notion("통합 테스트", "내용", uploaded_map)
        
        self.assertEqual(result['status'], 'success')
        print("✅ 전체 워크플로우 통합 테스트 통과")
    
    @patch('src.adapters.notion_api.requests.post')
    def test_notion_agent_workflow(self, mock_post):
        """Notion Agent 워크플로우 테스트 (upload_to_notion 직접 테스트)"""
        # Mock 응답
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {'results': []}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 200
        mock_create_response.json.return_value = {
            'id': 'workflow-test-id',
            'url': 'https://notion.so/workflow-test'
        }
        
        mock_post.side_effect = [mock_search_response, mock_create_response]
        
        # upload_to_notion 함수 테스트 (post_to_notion은 function_tool이라 직접 호출 불가)
        result = upload_to_notion(
            title="워크플로우 테스트",
            content="테스트 내용입니다.",
            uploaded_map={}
        )
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['status'], 'success')
        print("✅ Notion Agent 워크플로우 테스트 통과")


async def main():
    """메인 테스트 함수"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            print("🧪 유닛 테스트 실행 중...")
            unittest.main(argv=[''], exit=False, verbosity=2)
        elif sys.argv[1] == "integration":
            await test_notion_basic()
        elif sys.argv[1] == "images":
            await test_notion_with_images()
        else:
            print("사용법: python test_notion_integration.py [unit|integration|images]")
    else:
        print("사용법: python test_notion_integration.py [unit|integration|images]")
        print("\n기본 유닛 테스트 실행:")
        unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    asyncio.run(main())

