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
        """Test numbered list parsing"""
        parser = MarkdownToNotionParser()
        content = "1. First\n2. Second"
        blocks = parser.parse(content, {})
        
        numbered_items = [b for b in blocks if b['type'] == 'numbered_list_item']
        self.assertEqual(len(numbered_items), 2)
        print("✅ Numbered list test passed")
    
    def test_parse_nested_lists(self):
        """Test nested list parsing"""
        parser = MarkdownToNotionParser()
        content = "1. First item\n- Sub item 1\n- Sub item 2\n2. Second item"
        blocks = parser.parse(content, {})
        
        numbered_items = [b for b in blocks if b['type'] == 'numbered_list_item']
        self.assertGreater(len(numbered_items), 0)
        
        # Check if first numbered item has children
        if numbered_items:
            first_item = numbered_items[0]
            self.assertIn('children', first_item['numbered_list_item'])
            children = first_item['numbered_list_item']['children']
            self.assertGreater(len(children), 0)
            self.assertEqual(children[0]['type'], 'bulleted_list_item')
        
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
        self.assertIn('numbered_list_item', block_types)
        self.assertIn('paragraph', block_types)
        
        print("✅ Mixed content test passed")
    
    def test_create_notion_blocks_function(self):
        """Test convenience function"""
        content = "# Test\nSome text"
        blocks = create_notion_blocks(content, {})
        
        self.assertGreater(len(blocks), 0)
        self.assertEqual(blocks[0]['type'], 'heading_1')
        print("✅ create_notion_blocks function test passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)

