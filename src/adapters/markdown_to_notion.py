"""Markdown to Notion converter"""

import re


class MarkdownToNotionParser:
    """Convert markdown content to Notion blocks"""
    
    def __init__(self):
        self.uploaded_map = {}
    
    def parse(self, content: str, uploaded_map: dict[str, str]) -> list[dict]:
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
    
    def _parse_rich_text(self, text: str) -> list[dict]:
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
    
    def _create_text_block(self, block_type: str, text: str, children: list[dict] = None) -> list[dict]:
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
            # Add children if provided (올바른 위치에)
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
    
    def _normalize_table_row(self, row: list[str], width: int) -> list[str]:
        """Normalize table row to match specified width (pad or truncate)"""
        if len(row) < width:
            return row + [''] * (width - len(row))
        elif len(row) > width:
            return row[:width]
        return row
    
    def _create_table_block(self, lines: list[str]) -> dict:
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
    
    
    def _convert_header(self, line: str) -> list[dict]:
        """
        Convert header line to Notion block
        
        HEADER Processing Method (Simple 1:1 Conversion):
        - Header 1-3: Direct conversion to Notion's heading_1, heading_2, heading_3 blocks
        - Header 4-6: Converted to paragraph blocks due to Notion API limitations (bold + indent)
        - Characteristics: Process each line independently, no nested structure
        - Reason: Notion API only supports heading_1, heading_2, heading_3, so h4-h6 must be converted to paragraphs
        """
        # Check for h4-h6 first (convert to bold paragraphs)
        heading_match = re.match(r'^(#{4,6})\s+(.+)', line)
        if heading_match:
            level = len(heading_match.group(1))  # 4, 5, or 6
            text = heading_match.group(2)
            indent = "  " * (level - 3)  # 2, 4, or 6 spaces
            return [{
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{
                        'type': 'text',
                        'text': {'content': f"{indent}{text}"},
                        'annotations': {'bold': True}
                    }]
                }
            }]
        elif line.startswith('### '):
            return self._create_text_block('heading_3', line[4:])
        elif line.startswith('## '):
            return self._create_text_block('heading_2', line[3:])
        elif line.startswith('# '):
            return self._create_text_block('heading_1', line[2:])
        return []
    
    def _convert_numbered_list(self, line: str) -> list[dict]:
        """
        Convert numbered list line to Notion block
        
        NUMBERED LIST Processing Method (Simple 1:1 Conversion):
        - Numbered items: Converted to Notion paragraph blocks (with numbers included)
        - Characteristics: Process each line independently, no nested structure
        - Reason: Notion API doesn't properly handle children structure for numbered_list_item
        - Notion API Limitation: numbered_list_item blocks lose their children when uploaded to Notion
        """
        match = re.match(r'^\s*(\d+)\.\s+(.+)', line)
        if match:
            number = match.group(1)
            text = match.group(2)
            paragraph_text = f"{number}. {text}"
            return self._create_text_block('paragraph', paragraph_text)
        return []
    
    def _convert_bullet_list(self, line: str, lines: list[str], start_index: int) -> tuple[list[dict], int]:
        """
        Convert bullet list with proper children structure (unlimited nesting)
        
        BULLET LIST Processing Method (Complex Nested Structure Handling):
        - Characteristics: Process multiple lines together to understand nested structure
        - Recursive processing: Recursively process sub-bullets to support unlimited nesting
        - Children structure: Use Notion API's children property to implement nested structure
        - Mixed structure: Handle both bullets and numbered items together (Bullet + Number mixed)
        - Notion API Limitation: bulleted_list_item blocks also lose their children when uploaded to Notion
        
        Why different approach?
        1. HEADER/NUMBERED: Simple 1:1 conversion (process each line independently)
        2. BULLET: Complex nested structure (process multiple lines together to understand hierarchy)
        - Note: Despite Notion API limitations, we still build the children structure for completeness
        """
        text = re.sub(r'^\s*[-*]\s+', '', line)
        current_indent = len(line) - len(line.lstrip())
        
        # Collect sub-bullets (unlimited nesting allowed)
        children = []
        next_index = start_index + 1
        
        while next_index < len(lines):
            next_line = lines[next_index]
            if not next_line.strip():
                next_index += 1
                continue
                
            next_indent = len(next_line) - len(next_line.lstrip())
            
            # Break if same level or higher level
            if next_indent <= current_indent:
                break
                
            # Sub-bullet case
            if re.match(r'^\s*[-*]\s', next_line):
                child_text = re.sub(r'^\s*[-*]\s+', '', next_line)
                # Recursively process sub-bullets (unlimited nesting)
                child_blocks, next_index = self._convert_bullet_list(next_line, lines, next_index)
                children.extend(child_blocks)
            # Sub-numbered item case
            elif re.match(r'^\s*\d+\.\s', next_line):
                # Process numbered item as paragraph
                child_text = re.sub(r'^\s*\d+\.\s+', '', next_line)
                child_block = self._create_text_block('paragraph', f"{re.match(r'^\s*(\d+)\.\s', next_line).group(1)}. {child_text}")
                children.extend(child_block)
                next_index += 1
            else:
                break
        
        return self._create_text_block('bulleted_list_item', text, children), next_index
    
    def _convert_table(self, lines: list[str], start_index: int) -> tuple[dict, int]:
        """Convert table lines to Notion block"""
        # Find all table lines
        table_lines = []
        j = start_index
        while j < len(lines) and '|' in lines[j] and lines[j].strip().startswith('|'):
            table_lines.append(lines[j])
            j += 1
        
        # Create table block
        if len(table_lines) >= 2:  # At least header and one data row
            table_block = self._create_table_block(table_lines)
            return table_block, j
        else:
            # If not enough lines for table, treat as code
            return {
                'object': 'block',
                'type': 'code',
                'code': {
                    'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table_lines)}}],
                    'language': 'plain text'
                }
            }, j
    
    def _create_blocks_from_lines(self, lines: list[str]) -> list[dict]:
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
                table_block, next_index = self._convert_table(lines, i)
                children.append(table_block)
                processed_lines.update(range(i, next_index))
                continue
            
            # Headings
            if line.startswith('#'):
                children.extend(self._convert_header(line))
                continue
            
            # Numbered list
            if re.match(r'^\s*\d+\.\s', line):
                children.extend(self._convert_numbered_list(line))
                continue
            
            # Bullet list
            if re.match(r'^\s*[-*]\s', line):
                bullet_blocks, next_index = self._convert_bullet_list(line, lines, i)
                children.extend(bullet_blocks)
                processed_lines.update(range(i, next_index))
                continue
            # Paragraph
            else:
                children.extend(self._create_text_block('paragraph', line))
        
        return children
    
    def _create_image_block(self, image_url: str) -> dict:
        """Create Notion embed block for image"""
        return {
            'object': 'block',
            'type': 'embed',
            'embed': {'url': image_url}
        }


# Convenience function for backward compatibility
def create_notion_blocks(content: str, uploaded_map: dict[str, str]) -> list[dict]:
    """Parse markdown content into Notion blocks (convenience function)"""
    parser = MarkdownToNotionParser()
    return parser.parse(content, uploaded_map)

