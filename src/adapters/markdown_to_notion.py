"""Markdown to Notion converter"""

import re
from typing import List, Dict


class MarkdownToNotionParser:
    """Convert markdown content to Notion blocks"""
    
    def __init__(self):
        self.uploaded_map = {}
    
    def parse(self, content: str, uploaded_map: Dict[str, str]) -> List[Dict]:
        """Main entry point: parse markdown content into Notion blocks"""
        self.uploaded_map = uploaded_map
        children = []
        
        # Split content by image placeholders
        parts = re.split(r'(\{\{IMAGE_PLACEHOLDER:[^}]+\}\})', content)
        
        for part in parts:
            # Image placeholder
            if m := re.match(r'\{\{IMAGE_PLACEHOLDER:([^}]+)\}\}', part):
                file_path = m.group(1)
                if url := self.uploaded_map.get(file_path):
                    children.append(self._create_image_block(url))
                continue
            
            # Text content
            lines = part.split('\n')
            children.extend(self._create_blocks_from_lines(lines))
        
        return children
    
    def _parse_rich_text(self, text: str) -> List[Dict]:
        """Parse markdown text into Notion rich_text array (bold, italic, code only)"""
        rich_texts = []
        
        # Pattern: ***bold italic***, **bold**, *italic*, `code`
        # Order matters: bold italic must come before bold
        pattern = r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`)'
        parts = re.split(pattern, text)
        
        for part in parts:
            if not part:
                continue
            
            # Bold Italic: ***text***
            if part.startswith('***') and part.endswith('***'):
                rich_texts.append({
                    'type': 'text',
                    'text': {'content': part[3:-3]},
                    'annotations': {'bold': True, 'italic': True}
                })
            # Bold: **text**
            elif part.startswith('**') and part.endswith('**'):
                rich_texts.append({
                    'type': 'text',
                    'text': {'content': part[2:-2]},
                    'annotations': {'bold': True}
                })
            # Italic: *text* (but not **text** or ***text***)
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                rich_texts.append({
                    'type': 'text',
                    'text': {'content': part[1:-1]},
                    'annotations': {'italic': True}
                })
            # Code: `text`
            elif part.startswith('`') and part.endswith('`'):
                rich_texts.append({
                    'type': 'text',
                    'text': {'content': part[1:-1]},
                    'annotations': {'code': True}
                })
            # Plain text
            else:
                rich_texts.append({
                    'type': 'text',
                    'text': {'content': part}
                })
        
        return rich_texts if rich_texts else [{'type': 'text', 'text': {'content': ''}}]
    
    def _create_text_block(self, block_type: str, text: str, children: List[Dict] = None) -> List[Dict]:
        """Convert text to Notion block with markdown parsing and length limits"""
        blocks = []
        rich_text = self._parse_rich_text(text)
        
        # If total length exceeds 2000 chars, split into multiple blocks
        total_length = sum(len(rt['text']['content']) for rt in rich_text)
        
        if total_length <= 2000:
            block = {
                'object': 'block',
                'type': block_type,
                block_type: {'rich_text': rich_text}
            }
            # Add children if provided
            if children:
                block[block_type]['children'] = children
            blocks.append(block)
        else:
            # Split rich_text array when exceeding 2000 chars
            current_rich_texts = []
            current_length = 0
            
            for rt in rich_text:
                rt_length = len(rt['text']['content'])
                if current_length + rt_length > 2000 and current_rich_texts:
                    # Complete current block and start new one
                    block = {
                        'object': 'block',
                        'type': block_type,
                        block_type: {'rich_text': current_rich_texts}
                    }
                    # Add children to first block only
                    if children and not blocks:
                        block[block_type]['children'] = children
                    blocks.append(block)
                    current_rich_texts = []
                    current_length = 0
                
                current_rich_texts.append(rt)
                current_length += rt_length
            
            # Add remaining
            if current_rich_texts:
                block = {
                    'object': 'block',
                    'type': block_type,
                    block_type: {'rich_text': current_rich_texts}
                }
                # Add children to last block if no previous blocks
                if children and not blocks:
                    block[block_type]['children'] = children
                blocks.append(block)
        
        return blocks
    
    def _normalize_table_row(self, row: List[str], width: int) -> List[str]:
        """Normalize table row to match specified width (pad or truncate)"""
        if len(row) < width:
            return row + [''] * (width - len(row))
        elif len(row) > width:
            return row[:width]
        return row
    
    def _create_table_block(self, lines: List[str]) -> Dict:
        """Create Notion table block from markdown table lines"""
        # Extract header and data rows
        header_row = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        data_rows = []
        
        for row in lines[2:]:  # Skip header and separator lines
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if cells:
                data_rows.append(cells)
        
        if not data_rows:
            # Fallback to code block if no data
            return {
                'object': 'block',
                'type': 'code',
                'code': {
                    'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(lines)}}],
                    'language': 'plain text'
                }
            }
        
        # Normalize all rows to match header width
        table_width = len(header_row)
        header_row = self._normalize_table_row(header_row, table_width)
        data_rows = [self._normalize_table_row(row, table_width) for row in data_rows]
        
        # Create table block
        table_block = {
            'object': 'block',
            'type': 'table',
            'table': {
                'table_width': table_width,
                'has_column_header': True,
                'has_row_header': False,
                'children': []
            }
        }
        
        # Add header row
        header_cells = [self._parse_rich_text(cell) for cell in header_row]
        table_block['table']['children'].append({
            'object': 'block',
            'type': 'table_row',
            'table_row': {'cells': header_cells}
        })
        
        # Add data rows
        for row in data_rows:
            row_cells = [self._parse_rich_text(cell) for cell in row]
            table_block['table']['children'].append({
                'object': 'block',
                'type': 'table_row',
                'table_row': {'cells': row_cells}
            })
        
        return table_block
    
    def _parse_nested_bullets(self, lines: List[str], start_index: int, parent_indent: int) -> tuple[List[Dict], int]:
        """
        Parse nested bullet points based on indentation.
        - Tab/spaces in markdown → children in Notion
        - No depth limit - just follow indentation
        """
        items = []
        i = start_index
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # Stop if we've returned to parent level or higher
            if indent <= parent_indent:
                break
            
            # Only process bullets that are direct children
            if not re.match(r'^\s*[-*]\s', line):
                i += 1
                continue
            
            # Extract text
            text = re.sub(r'^\s*[-*]\s+', '', line)
            
            # Recursively parse children (based on indent only)
            children, next_i = self._parse_nested_bullets(lines, i + 1, indent)
            
            # Create bullet with or without children
            items.extend(self._create_text_block('bulleted_list_item', text, children))
            i = next_i
        
        return items, i
    
    
    def _create_blocks_from_lines(self, lines: List[str]) -> List[Dict]:
        """Parse lines into Notion blocks - Pythonic approach"""
        children = []
        processed_lines = set()
        
        for i, line in enumerate(lines):
            if i in processed_lines or not line.strip():
                continue
            
            # Code block (```language)
            if line.startswith('```'):
                language = line[3:].strip() or 'plain text'
                code_lines = []
                
                # Find closing ```
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('```'):
                        processed_lines.update(range(i, j + 1))
                        break
                    code_lines.append(lines[j])
                
                children.append({
                    'object': 'block',
                    'type': 'code',
                    'code': {
                        'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(code_lines)}}],
                        'language': language
                    }
                })
                continue
            
            # Table
            if line.startswith('|'):
                table_lines = []
                for j in range(i, len(lines)):
                    if not lines[j].startswith('|'):
                        break
                    table_lines.append(lines[j])
                    processed_lines.add(j)
                
                if len(table_lines) >= 2:
                    children.append(self._create_table_block(table_lines))
                else:
                    children.append({
                        'object': 'block',
                        'type': 'code',
                        'code': {
                            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table_lines)}}],
                            'language': 'plain text'
                        }
                    })
                continue
            
            # Headings (Notion only supports up to heading_3)
            # Check for h4-h6 first (convert to bold paragraphs with bullets)
            heading_match = re.match(r'^(#{4,6})\s+(.+)', line)
            if heading_match:
                level = len(heading_match.group(1))  # 4, 5, or 6
                text = heading_match.group(2)
                indent = "  " * (level - 3)  # 2, 4, or 6 spaces
                children.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{
                            'type': 'text',
                            'text': {'content': f"{indent}• {text}"},
                            'annotations': {'bold': True}
                        }]
                    }
                })
            elif line.startswith('### '):
                children.extend(self._create_text_block('heading_3', line[4:]))
            elif line.startswith('## '):
                children.extend(self._create_text_block('heading_2', line[3:]))
            elif line.startswith('# '):
                children.extend(self._create_text_block('heading_1', line[2:]))
            # Numbered list - convert to paragraph (no bullet point)
            elif re.match(r'^\s*\d+\.\s', line):
                # Extract number and text
                match = re.match(r'^\s*(\d+)\.\s+(.+)', line)
                if match:
                    number = match.group(1)
                    text = match.group(2)
                    paragraph_text = f"{number}. {text}"
                    
                    # Convert to paragraph (no bullet point)
                    children.extend(self._create_text_block('paragraph', paragraph_text))
            # Bullet list - with nesting based on indentation
            elif re.match(r'^\s*[-*]\s', line):
                text = re.sub(r'^\s*[-*]\s+', '', line)
                current_indent = len(line) - len(line.lstrip())
                
                # Parse nested bullets (based on indent only)
                nested_items, next_index = self._parse_nested_bullets(lines, i + 1, current_indent)
                
                # Create bullet with children
                children.extend(self._create_text_block('bulleted_list_item', text, nested_items))
                
                # Update processed lines
                processed_lines.update(range(i, next_index))
            # Paragraph
            else:
                children.extend(self._create_text_block('paragraph', line))
        
        return children
    
    def _create_image_block(self, image_url: str) -> Dict:
        """Create Notion embed block for image"""
        return {
            'object': 'block',
            'type': 'embed',
            'embed': {'url': image_url}
        }


# Convenience function for backward compatibility
def create_notion_blocks(content: str, uploaded_map: Dict[str, str]) -> List[Dict]:
    """Parse markdown content into Notion blocks (convenience function)"""
    parser = MarkdownToNotionParser()
    return parser.parse(content, uploaded_map)

