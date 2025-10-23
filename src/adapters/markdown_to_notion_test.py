#!/usr/bin/env python3
"""MarkdownToNotionParser unit tests"""

import unittest
from src.adapters.markdown_to_notion import MarkdownToNotionParser, create_notion_blocks


class TestMarkdownToNotionParser(unittest.TestCase):
    """MarkdownToNotionParser class tests"""
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        parser = MarkdownToNotionParser()
        self.assertIsNotNone(parser)
        self.assertEqual(parser.uploaded_map, {})
        print("✅ Parser initialization test passed")
    
    def test_parse_method(self):
        """Test parse method"""
        parser = MarkdownToNotionParser()
        content = "# Test Heading\nSome text"
        blocks = parser.parse(content, {})
        
        self.assertGreater(len(blocks), 0)
        self.assertEqual(blocks[0]['type'], 'heading_1')
        print("✅ Parse method test passed")
    
    def test_rich_text_formatting(self):
        """Test rich text formatting parsing"""
        parser = MarkdownToNotionParser()
        
        # Test bold
        bold_text = parser._parse_rich_text("**bold text**")
        self.assertEqual(bold_text[0]['annotations']['bold'], True)
        
        # Test italic
        italic_text = parser._parse_rich_text("*italic text*")
        self.assertEqual(italic_text[0]['annotations']['italic'], True)
        
        # Test bold italic
        bold_italic_text = parser._parse_rich_text("***bold italic***")
        self.assertEqual(bold_italic_text[0]['annotations']['bold'], True)
        self.assertEqual(bold_italic_text[0]['annotations']['italic'], True)
        
        # Test code
        code_text = parser._parse_rich_text("`code text`")
        self.assertEqual(code_text[0]['annotations']['code'], True)
        
        print("✅ Rich text formatting test passed")
    
    def test_parse_heading_1(self):
        """Test heading 1 parsing"""
        parser = MarkdownToNotionParser()
        content = "# Main Title"
        blocks = parser.parse(content, {})
        
        self.assertEqual(blocks[0]['type'], 'heading_1')
        self.assertIn('Main Title', blocks[0]['heading_1']['rich_text'][0]['text']['content'])
        print("✅ Heading 1 test passed")
    
    def test_parse_heading_2(self):
        """Test heading 2 parsing"""
        parser = MarkdownToNotionParser()
        content = "## Section Title"
        blocks = parser.parse(content, {})
        
        self.assertEqual(blocks[0]['type'], 'heading_2')
        self.assertIn('Section Title', blocks[0]['heading_2']['rich_text'][0]['text']['content'])
        print("✅ Heading 2 test passed")
    
    def test_parse_heading_3(self):
        """Test heading 3 parsing"""
        parser = MarkdownToNotionParser()
        content = "### Subsection Title"
        blocks = parser.parse(content, {})
        
        self.assertEqual(blocks[0]['type'], 'heading_3')
        self.assertIn('Subsection Title', blocks[0]['heading_3']['rich_text'][0]['text']['content'])
        print("✅ Heading 3 test passed")
    
    def test_parse_bullet_list(self):
        """Test bullet list parsing"""
        parser = MarkdownToNotionParser()
        content = "- Item 1\n- Item 2"
        blocks = parser.parse(content, {})
        
        bullet_items = [b for b in blocks if b['type'] == 'bulleted_list_item']
        self.assertEqual(len(bullet_items), 2)
        print("✅ Bullet list test passed")
    
    def test_parse_numbered_list(self):
        """Test numbered list parsing (now converted to paragraph)"""
        parser = MarkdownToNotionParser()
        content = "1. First\n2. Second"
        blocks = parser.parse(content, {})
        
        # Numbered lists are now converted to paragraph
        paragraph_items = [b for b in blocks if b['type'] == 'paragraph']
        self.assertEqual(len(paragraph_items), 2)
        self.assertEqual(paragraph_items[0]['paragraph']['rich_text'][0]['text']['content'], '1. First')
        self.assertEqual(paragraph_items[1]['paragraph']['rich_text'][0]['text']['content'], '2. Second')
        print("✅ Numbered list test passed")
    
    def test_parse_nested_lists(self):
        """Test nested list parsing with proper indentation"""
        parser = MarkdownToNotionParser()
        content = """1. First item
   - Sub item 1
   - Sub item 2
2. Second item"""
        blocks = parser.parse(content, {})
        
        # Numbered lists are now paragraph, bullets remain as bullets
        paragraph_items = [b for b in blocks if b['type'] == 'paragraph']
        bullet_items = [b for b in blocks if b['type'] == 'bulleted_list_item']
        
        self.assertEqual(len(paragraph_items), 2)
        self.assertEqual(len(bullet_items), 2)
        
        print("✅ Nested lists test passed")
    
    def test_parse_code_block(self):
        """Test code block parsing"""
        parser = MarkdownToNotionParser()
        content = "```python\ndef hello():\n    print('hello')\n```"
        blocks = parser.parse(content, {})
        
        code_blocks = [b for b in blocks if b['type'] == 'code']
        self.assertGreater(len(code_blocks), 0)
        
        if code_blocks:
            code_block = code_blocks[0]
            self.assertEqual(code_block['code']['language'], 'python')
            self.assertIn('def hello()', code_block['code']['rich_text'][0]['text']['content'])
        
        print("✅ Code block test passed")
    
    def test_parse_table(self):
        """Test table parsing"""
        parser = MarkdownToNotionParser()
        content = "| Header1 | Header2 |\n|---------|----------|\n| Value1  | Value2   |"
        blocks = parser.parse(content, {})
        
        table_blocks = [b for b in blocks if b['type'] == 'table']
        self.assertGreater(len(table_blocks), 0)
        
        if table_blocks:
            table = table_blocks[0]['table']
            self.assertEqual(table['table_width'], 2)
            self.assertTrue(table['has_column_header'])
        
        print("✅ Table test passed")
    
    def test_parse_image_placeholder(self):
        """Test image placeholder replacement"""
        parser = MarkdownToNotionParser()
        content = "Text before\n{{IMAGE_PLACEHOLDER:/tmp/test.png}}\nText after"
        uploaded_map = {"/tmp/test.png": "https://example.com/image.jpg"}
        
        blocks = parser.parse(content, uploaded_map)
        
        embed_blocks = [b for b in blocks if b['type'] == 'embed']
        self.assertGreater(len(embed_blocks), 0)
        
        if embed_blocks:
            self.assertEqual(embed_blocks[0]['embed']['url'], "https://example.com/image.jpg")
        
        print("✅ Image placeholder test passed")
    
    def test_parse_mixed_content(self):
        """Test parsing mixed content types"""
        parser = MarkdownToNotionParser()
        content = """# Title
## Section
- Bullet 1
- Bullet 2
1. Numbered 1
2. Numbered 2
**Bold** and *italic* text
`inline code`
"""
        blocks = parser.parse(content, {})
        
        block_types = [b['type'] for b in blocks]
        self.assertIn('heading_1', block_types)
        self.assertIn('heading_2', block_types)
        self.assertIn('bulleted_list_item', block_types)
        # numbered lists are now paragraph (no special type needed)
        self.assertIn('paragraph', block_types)
        
        print("✅ Mixed content test passed")
    
    def test_create_notion_blocks_function(self):
        """Test convenience function"""
        content = "# Test\nSome text"
        blocks = create_notion_blocks(content, {})
        
        self.assertGreater(len(blocks), 0)
        self.assertEqual(blocks[0]['type'], 'heading_1')
        print("✅ create_notion_blocks function test passed")
    
    def test_complex_nested_structure(self):
        """Test complex nested numbered and bulleted lists structure"""
        parser = MarkdownToNotionParser()
        content = """# 종합 유동성 평가

1. 분석 통합
   1. 주요 유동성 트렌드 및 동인
      • 국채 수익률: 6개월 동안 수익률이 -8.98%로 큰 폭으로 하락했으며, 이는 시장의 불확실성이 높아졌음을 나타냅니다.
      • NFCI 지수: 최근 5개월간 -0.539에서 -0.552로 감소하여 금융 조건이 여전히 완화되고 있으며, 앞으로도 지속될 것으로 예상됩니다.

2. 위험 자산에 대한 시장 영향 평가
   1. 투자자에 대한 전략적 통찰
      • 포트폴리오 다각화: 유동성이 완화되는 시점에서 포트폴리오 내 위험 자산의 비중을 늘리는 것이 전략적으로 유리할 수 있습니다.
      • 전문 종목 선정: 안정성이 높은 기업의 주식이나 기술주와 같이 성장 가능성이 높은 섹터에 대한 집중 투자를 고려해볼 수 있습니다.
      • 헷지 전략: 만약 급격한 금리 인상이나 경제적 불확실성이 우려되는 경우, 헷지 전략을 통한 리스크 관리가 필요할 수 있습니다.
"""
        blocks = parser.parse(content, {})
        
        # Check structure: heading + heading_3s (numbered lists) + bullets
        self.assertGreater(len(blocks), 0)
        self.assertEqual(blocks[0]['type'], 'heading_1')
        
        # Check paragraph items (numbered lists now converted to paragraph)
        paragraph_items = [b for b in blocks if b['type'] == 'paragraph']
        self.assertGreater(len(paragraph_items), 0)
        
        # Check paragraph items (bullet items are now converted to paragraph)
        paragraph_items = [b for b in blocks if b['type'] == 'paragraph']
        self.assertGreater(len(paragraph_items), 0)
        
        print("✅ Complex nested structure test passed")
    
    def test_heading_levels(self):
        """Test all heading levels (Notion only supports up to heading_3)"""
        parser = MarkdownToNotionParser()
        content = """# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6"""
        blocks = parser.parse(content, {})
        
        # Check that we have 6 blocks
        self.assertEqual(len(blocks), 6)
        
        # Check types (h1-h3 are headings, h4+ are bold paragraphs)
        self.assertEqual(blocks[0]['type'], 'heading_1')
        self.assertEqual(blocks[1]['type'], 'heading_2')
        self.assertEqual(blocks[2]['type'], 'heading_3')
        self.assertEqual(blocks[3]['type'], 'paragraph')  # heading_4 -> bold paragraph
        self.assertEqual(blocks[4]['type'], 'paragraph')  # heading_5 -> bold paragraph
        self.assertEqual(blocks[5]['type'], 'paragraph')  # heading_6 -> bold paragraph
        
        # Check text content for h1-h3
        self.assertEqual(blocks[0]['heading_1']['rich_text'][0]['text']['content'], 'Heading 1')
        self.assertEqual(blocks[1]['heading_2']['rich_text'][0]['text']['content'], 'Heading 2')
        self.assertEqual(blocks[2]['heading_3']['rich_text'][0]['text']['content'], 'Heading 3')
        
        # Check h4-h6 are bold paragraphs with bullets and indentation
        self.assertIn('• Heading 4', blocks[3]['paragraph']['rich_text'][0]['text']['content'])
        self.assertTrue(blocks[3]['paragraph']['rich_text'][0]['annotations']['bold'])
        
        self.assertIn('• Heading 5', blocks[4]['paragraph']['rich_text'][0]['text']['content'])
        self.assertTrue(blocks[4]['paragraph']['rich_text'][0]['annotations']['bold'])
        
        self.assertIn('• Heading 6', blocks[5]['paragraph']['rich_text'][0]['text']['content'])
        self.assertTrue(blocks[5]['paragraph']['rich_text'][0]['annotations']['bold'])
        
        print("✅ Heading levels test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)

