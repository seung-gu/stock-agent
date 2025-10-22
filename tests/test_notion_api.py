#!/usr/bin/env python3
"""Notion API 어댑터 유닛 테스트"""

import unittest
from unittest.mock import patch, MagicMock
from src.adapters.notion_api import create_notion_blocks, upload_to_notion


class TestNotionAPI(unittest.TestCase):
    """Notion API 함수 테스트"""
    
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
    
    def test_create_notion_blocks_markdown_headings(self):
        """마크다운 헤딩 파싱 테스트"""
        content = """
# 제목 1
## 제목 2
### 제목 3
일반 텍스트
"""
        blocks = create_notion_blocks(content, {})
        
        block_types = [block['type'] for block in blocks]
        self.assertIn('heading_1', block_types)
        self.assertIn('heading_2', block_types)
        self.assertIn('heading_3', block_types)
        self.assertIn('paragraph', block_types)
        print("✅ 마크다운 헤딩 파싱 테스트 통과")
    
    def test_create_notion_blocks_lists(self):
        """리스트 파싱 테스트"""
        content = """
- 항목 1
- 항목 2
1. 번호 항목 1
2. 번호 항목 2
"""
        blocks = create_notion_blocks(content, {})
        
        block_types = [block['type'] for block in blocks]
        self.assertIn('bulleted_list_item', block_types)
        self.assertIn('numbered_list_item', block_types)
        print("✅ 리스트 파싱 테스트 통과")
    
    def test_create_notion_blocks_tables(self):
        """테이블 파싱 테스트"""
        content = """
| 헤더1 | 헤더2 |
|-------|-------|
| 값1   | 값2   |
| 값3   | 값4   |
"""
        blocks = create_notion_blocks(content, {})
        
        table_blocks = [b for b in blocks if b['type'] == 'table']
        self.assertGreater(len(table_blocks), 0)
        
        if table_blocks:
            table = table_blocks[0]['table']
            self.assertEqual(table['table_width'], 2)
            self.assertTrue(table['has_column_header'])
        print("✅ 테이블 파싱 테스트 통과")
    
    @patch('src.adapters.notion_api.requests.post')
    def test_upload_to_notion_new_page(self, mock_post):
        """Notion 새 페이지 생성 테스트"""
        # Mock 응답 설정 - 검색 결과 없음 (새 페이지 생성)
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {'results': []}
        
        mock_create_response = MagicMock()
        mock_create_response.status_code = 200
        mock_create_response.json.return_value = {'url': 'https://notion.so/new-page'}
        
        mock_post.side_effect = [mock_search_response, mock_create_response]
        
        uploaded_map = {"/tmp/test.png": "https://example.com/image.jpg"}
        result = upload_to_notion("테스트 제목", "내용", uploaded_map)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('url', result)
        print("✅ upload_to_notion (새 페이지) 테스트 통과")
    
    @patch('src.adapters.notion_api.requests.patch')
    @patch('src.adapters.notion_api.requests.post')
    def test_upload_to_notion_existing_page(self, mock_post, mock_patch):
        """Notion 기존 페이지 업데이트 테스트"""
        # Mock 응답 설정 - 기존 페이지 발견
        mock_search_response = MagicMock()
        mock_search_response.status_code = 200
        mock_search_response.json.return_value = {
            'results': [{
                'id': 'existing-page-id',
                'url': 'https://notion.so/existing-page',
                'properties': {
                    'title': {
                        'title': [{'text': {'content': '테스트 제목'}}]
                    }
                }
            }]
        }
        mock_post.return_value = mock_search_response
        
        mock_patch_response = MagicMock()
        mock_patch_response.status_code = 200
        mock_patch.return_value = mock_patch_response
        
        uploaded_map = {}
        result = upload_to_notion("테스트 제목", "업데이트 내용", uploaded_map)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('url', result)
        print("✅ upload_to_notion (기존 페이지) 테스트 통과")


if __name__ == "__main__":
    unittest.main(verbosity=2)

