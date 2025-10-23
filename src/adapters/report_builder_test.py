#!/usr/bin/env python3
"""Report Builder 통합 테스트 및 E2E 테스트"""

import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv
from src.adapters.report_builder import upload_report_with_children

# 환경변수 로드
load_dotenv()


def test_report_with_children():
    """리포트 업로드 테스트 (부모 + 자식 페이지)"""
    import os
    
    if not os.environ.get('NOTION_API_KEY') or not os.environ.get('NOTION_DATABASE_ID'):
        print("⚠️ Skipping test - Notion credentials not set")
        return
    
    print("=" * 80)
    print("🧪 Report Builder 테스트 시작...")
    print("=" * 80)
    
    child_pages = [
        ("Liquidity Analysis", "# Liquidity Analysis\n\nTest content."),
        ("Equity Analysis", "# Equity Analysis\n\nTest content."),
        ("Conclusion & Insights", "# Conclusion\n\nTest insights.")
    ]
    
    result = upload_report_with_children(
        title="Test Report",
        date="2025-01-20",
        summary="This is a test report",
        child_pages=child_pages,
        uploaded_map={}
    )
    
    print("\n" + "=" * 80)
    if result['status'] == 'success':
        print("✅ Report Builder 테스트 완료!")
        print(f"   URL: {result['url']}")
    else:
        print(f"❌ Test failed: {result}")
    print("=" * 80)


class TestReportBuilder(unittest.TestCase):
    """Report Builder 유닛 테스트"""
    
    @patch('src.adapters.report_builder.upload_to_notion')
    @patch('src.adapters.report_builder.create_child_page')
    @patch('src.adapters.report_builder.find_local_images')
    def test_template_structure(self, mock_find_images, mock_create_child, mock_upload):
        """템플릿 구조 테스트"""
        # Mock 설정
        mock_find_images.return_value = ("processed", [], {})
        mock_upload.return_value = {"status": "success", "page_id": "parent-123", "url": "https://notion.so/test"}
        mock_create_child.return_value = {"status": "success", "url": "https://notion.so/child"}
        
        child_pages = [
            ("Test Child", "Content")
        ]
        
        result = upload_report_with_children(
            title="Test Title",
            date="2025-01-20",
            summary="Test summary",
            child_pages=child_pages,
            uploaded_map={}
        )
        
        # upload_to_notion이 호출되었는지 확인
        self.assertTrue(mock_upload.called)
        
        # create_child_page이 호출되었는지 확인
        self.assertTrue(mock_create_child.called)
        
        # 결과 확인
        self.assertEqual(result['status'], 'success')
        print("✅ Template structure test passed")
    
    @patch('src.adapters.report_builder.upload_to_notion')
    def test_parent_page_creation_failure(self, mock_upload):
        """부모 페이지 생성 실패 테스트"""
        mock_upload.return_value = {"status": "error", "message": "Failed"}
        
        result = upload_report_with_children(
            title="Test",
            date="2025-01-20",
            summary="Summary",
            child_pages=[],
            uploaded_map={}
        )
        
        self.assertEqual(result['status'], 'error')
        print("✅ Parent page failure test passed")


async def main():
    """메인 테스트 함수"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            print("🧪 유닛 테스트 실행 중...")
            unittest.main(argv=[''], exit=False, verbosity=2)
        elif sys.argv[1] == "integration":
            test_report_with_children()
        else:
            print("사용법: python report_builder_test.py [unit|integration]")
    else:
        print("사용법: python report_builder_test.py [unit|integration]")
        print("\n기본 유닛 테스트 실행:")
        unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

