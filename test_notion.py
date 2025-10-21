#!/usr/bin/env python3
"""Notion Agent 테스트 스크립트"""

import asyncio
import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from agents import Runner
from src.agent.notion_agent import (
    notion_agent, 
    find_local_images, 
    upload_images_to_cloudflare, 
    create_notion_blocks, 
    upload_to_notion
)

# 환경변수 로드
load_dotenv()

async def test_notion_basic():
    """기본 Notion 업로드 테스트"""
    
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
    """이미지 포함 Notion 업로드 테스트"""
    
    test_title = "이미지 테스트 리포트"
    test_content = """
# 이미지 테스트

이것은 Notion 이미지 업로드 테스트입니다.

## 차트 이미지들이 아래에 표시되어야 합니다:

![TNX 5일 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_5_days_chart.png)
![TNX 1개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_1_month_chart.png)
![TNX 6개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_6_months_chart.png)
![AAPL 5일 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_5_days_chart.png)
![AAPL 1개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_1_month_chart.png)
![AAPL 6개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_6_months_chart.png)

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

class TestNotionFunctions(unittest.TestCase):
    """Notion Agent 개별 함수 테스트"""
    
    @patch('src.agent.notion_agent.os.path.exists')
    def test_find_local_images(self, mock_exists):
        """로컬 이미지 찾기 함수 테스트"""
        # Mock 설정: 파일이 존재한다고 가정
        mock_exists.return_value = True
        
        test_content = """
# 테스트 리포트
![차트1](sandbox:/tmp/test1.png)
![차트2](sandbox:/tmp/test2.png)
테스트 완료!
"""
        processed_content, image_files, image_map = find_local_images(test_content)
        
        self.assertIn("테스트 완료!", processed_content)
        self.assertIn("{{IMAGE_PLACEHOLDER:/tmp/test1.png}}", processed_content)
        self.assertIn("{{IMAGE_PLACEHOLDER:/tmp/test2.png}}", processed_content)
        self.assertNotIn("![차트1]", processed_content)
        self.assertNotIn("![차트2]", processed_content)
        self.assertEqual(len(image_files), 2)
        self.assertEqual(len(image_map), 2)
        print("✅ find_local_images 테스트 통과")
    
    @patch('boto3.client')
    @patch('PIL.Image.open')
    def test_upload_images_to_cloudflare(self, mock_image_open, mock_boto3):
        """R2 이미지 업로드 함수 테스트"""
        # Mock 설정
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        test_files = ["/tmp/test1.png", "/tmp/test2.png"]
        result = upload_images_to_cloudflare(test_files)
        
        self.assertIsInstance(result, dict)
        print("✅ upload_images_to_cloudflare 테스트 통과")
    
    def test_create_notion_blocks(self):
        """Notion 블록 생성 함수 테스트"""
        content = "테스트 내용\n{{IMAGE_PLACEHOLDER:/tmp/test1.png}}\n추가 내용"
        uploaded_map = {"/tmp/test1.png": "https://example.com/image1.jpg"}
        
        blocks = create_notion_blocks(content, uploaded_map)
        
        self.assertGreater(len(blocks), 0)
        self.assertIn('paragraph', [block['type'] for block in blocks])
        self.assertIn('image', [block['type'] for block in blocks])
        print("✅ create_notion_blocks 테스트 통과")
    
    def test_create_notion_blocks_long_content(self):
        """긴 내용 Notion 블록 생성 테스트"""
        long_lines = '\n'.join(['테스트 내용입니다. ' * 30 for _ in range(10)])
        uploaded_map = {}
        
        blocks = create_notion_blocks(long_lines, uploaded_map)
        
        paragraph_blocks = [b for b in blocks if b['type'] == 'paragraph']
        self.assertGreater(len(paragraph_blocks), 1)
        print("✅ 긴 내용 블록 분할 테스트 통과")
    
    @patch('src.agent.notion_agent.requests.post')
    def test_upload_to_notion(self, mock_post):
        """Notion 업로드 함수 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'url': 'https://notion.so/test'}
        mock_post.return_value = mock_response
        
        uploaded_map = {"/tmp/test.png": "https://example.com/image.jpg"}
        result = upload_to_notion("테스트", "내용", uploaded_map)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('url', result)
        print("✅ upload_to_notion 테스트 통과")


class TestNotionIntegration(unittest.TestCase):
    """Notion Agent 통합 테스트"""
    
    @patch('requests.post')
    @patch('boto3.client')
    @patch('PIL.Image.open')
    def test_full_workflow(self, mock_image_open, mock_boto3, mock_post):
        """전체 워크플로우 통합 테스트"""
        # Mock 설정
        mock_img = MagicMock()
        mock_image_open.return_value.__enter__.return_value = mock_img
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'url': 'https://notion.so/test'}
        mock_post.return_value = mock_response
        
        # 테스트 실행
        uploaded_map = {"/tmp/test.png": "https://example.com/image.jpg"}
        result = upload_to_notion("통합 테스트", "내용", uploaded_map)
        
        self.assertEqual(result['status'], 'success')
        print("✅ 전체 워크플로우 통합 테스트 통과")


async def test_notion_basic():
    """기본 Notion 업로드 테스트"""
    
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
    """이미지 포함 Notion 업로드 테스트"""
    
    test_title = "이미지 테스트 리포트"
    test_content = """
# 이미지 테스트

이것은 Notion 이미지 업로드 테스트입니다.

## 차트 이미지들이 아래에 표시되어야 합니다:

![TNX 5일 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_5_days_chart.png)
![TNX 1개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_1_month_chart.png)
![TNX 6개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/TNX_6_months_chart.png)
![AAPL 5일 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_5_days_chart.png)
![AAPL 1개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_1_month_chart.png)
![AAPL 6개월 차트](sandbox:/var/folders/n6/c34rbztd6c1c_p9pfv1jbb340000gn/T/market_charts_0byvmm_9/AAPL_6_months_chart.png)

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

def run_unit_tests():
    """유닛 테스트 실행"""
    print("🧪 유닛 테스트 실행 중...")
    unittest.main(argv=[''], exit=False, verbosity=2)

async def run_integration_tests():
    """통합 테스트 실행"""
    print("🔄 통합 테스트 실행 중...")
    if len(sys.argv) > 1 and sys.argv[1] == "images":
        await test_notion_with_images()
    else:
        await test_notion_basic()

async def main():
    """메인 테스트 함수"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            run_unit_tests()
        elif sys.argv[1] == "integration":
            await run_integration_tests()
        elif sys.argv[1] == "images":
            await test_notion_with_images()
        else:
            print("사용법: python test_notion.py [unit|integration|images]")
    else:
        print("사용법: python test_notion.py [unit|integration|images]")

if __name__ == "__main__":
    asyncio.run(main())
