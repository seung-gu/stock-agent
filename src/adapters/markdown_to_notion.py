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
            lines = [l.strip() for l in part.split('\n')]
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
    
    def _create_text_block(self, block_type: str, text: str) -> List[Dict]:
        """Convert text to Notion block with markdown parsing and length limits"""
        blocks = []
        rich_text = self._parse_rich_text(text)
        
        # If total length exceeds 2000 chars, split into multiple blocks
        total_length = sum(len(rt['text']['content']) for rt in rich_text)
        
        if total_length <= 2000:
            blocks.append({
                'object': 'block',
                'type': block_type,
                block_type: {'rich_text': rich_text}
            })
        else:
            # Split rich_text array when exceeding 2000 chars
            current_rich_texts = []
            current_length = 0
            
            for rt in rich_text:
                rt_length = len(rt['text']['content'])
                if current_length + rt_length > 2000 and current_rich_texts:
                    # Complete current block and start new one
                    blocks.append({
                        'object': 'block',
                        'type': block_type,
                        block_type: {'rich_text': current_rich_texts}
                    })
                    current_rich_texts = []
                    current_length = 0
                
                current_rich_texts.append(rt)
                current_length += rt_length
            
            # Add remaining
            if current_rich_texts:
                blocks.append({
                    'object': 'block',
                    'type': block_type,
                    block_type: {'rich_text': current_rich_texts}
                })
        
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
    
    def _create_numbered_list_with_nested_bullets(
        self,
        text: str,
        lines: List[str],
        start_index: int
    ) -> tuple[List[Dict], int]:
        """Create numbered list item with nested bullets if any"""
        blocks = self._create_text_block('numbered_list_item', text)
        
        # Look ahead for bulleted items to nest as children
        nested_bullets = []
        j = start_index + 1
        
        while j < len(lines):
            next_line = lines[j]
            if not next_line:
                j += 1
                continue
            
            if re.match(r'^\s*[-*]\s', next_line):
                # This is a bullet to nest
                bullet_text = re.sub(r'^\s*[-*]\s+', '', next_line)
                nested_bullets.extend(self._create_text_block('bulleted_list_item', bullet_text))
                j += 1
            else:
                # Stop at non-bullet line
                break
        
        # Add nested bullets as children if any
        if nested_bullets:
            for block in blocks:
                if block['type'] == 'numbered_list_item':
                    block['numbered_list_item']['children'] = nested_bullets
            return blocks, j - 1  # Return blocks and skip processed bullets
        
        return blocks, start_index
    
    def _create_blocks_from_lines(self, lines: List[str]) -> List[Dict]:
        """Parse lines into Notion blocks"""
        children = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            if not line:
                i += 1
                continue
            
            # Code block (```language)
            if line.startswith('```'):
                code_lines = []
                language = line[3:].strip() or 'plain text'
                i += 1
                
                # Collect code until closing ```
                while i < len(lines):
                    if lines[i].startswith('```'):
                        i += 1
                        break
                    code_lines.append(lines[i])
                    i += 1
                
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
                while i < len(lines) and lines[i].startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                
                if len(table_lines) >= 2:
                    children.append(self._create_table_block(table_lines))
                else:
                    # Fallback to code block
                    children.append({
                        'object': 'block',
                        'type': 'code',
                        'code': {
                            'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table_lines)}}],
                            'language': 'plain text'
                        }
                    })
                continue
            
            # Headings
            if line.startswith('### '):
                children.extend(self._create_text_block('heading_3', line[4:]))
            elif line.startswith('## '):
                children.extend(self._create_text_block('heading_2', line[3:]))
            elif line.startswith('# '):
                children.extend(self._create_text_block('heading_1', line[2:]))
            # Numbered list
            elif re.match(r'^\s*\d+\.\s', line):
                text = re.sub(r'^\s*\d+\.\s+', '', line)
                blocks, next_index = self._create_numbered_list_with_nested_bullets(text, lines, i)
                children.extend(blocks)
                i = next_index
            # Bullet list
            elif re.match(r'^\s*[-*]\s', line):
                text = re.sub(r'^\s*[-*]\s+', '', line)
                children.extend(self._create_text_block('bulleted_list_item', text))
            # Paragraph
            else:
                children.extend(self._create_text_block('paragraph', line))
            
            i += 1
        
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

