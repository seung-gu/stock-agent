"""Notion API 어댑터 - Notion 페이지 생성 및 블록 관리"""

import os
import re
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv(override=True)


def parse_rich_text(text: str) -> list[dict]:
    """마크다운 텍스트를 Notion rich_text 배열로 파싱 (bold, italic, code만 처리)"""
    rich_texts = []
    
    # 패턴: **bold**, *italic*, `code` (링크는 제외 - URL 검증 문제 방지)
    pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`)'
    parts = re.split(pattern, text)
    
    for part in parts:
        if not part:
            continue
        
        # Bold: **text**
        if part.startswith('**') and part.endswith('**'):
            rich_texts.append({
                'type': 'text',
                'text': {'content': part[2:-2]},
                'annotations': {'bold': True}
            })
        # Italic: *text*
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


def create_notion_blocks(content: str, uploaded_map: dict[str, str]) -> list[dict]:
    """간단한 마크다운 파서로 Notion 블록 생성"""
    
    def make_block(block_type: str, text: str) -> list[dict]:
        """텍스트를 Notion 블록으로 변환 (마크다운 파싱 포함)"""
        blocks = []
        rich_text = parse_rich_text(text)
        
        # rich_text의 총 길이가 2000자를 넘으면 분할
        # 간단하게 처리: 전체 텍스트가 2000자를 넘으면 여러 블록으로
        total_length = sum(len(rt['text']['content']) for rt in rich_text)
        
        if total_length <= 2000:
            blocks.append({
                'object': 'block',
                'type': block_type,
                block_type: {'rich_text': rich_text}
            })
        else:
            # 2000자 넘으면 rich_text 배열을 나눔
            current_rich_texts = []
            current_length = 0
            
            for rt in rich_text:
                rt_length = len(rt['text']['content'])
                if current_length + rt_length > 2000 and current_rich_texts:
                    # 현재 블록을 완성하고 새 블록 시작
                    blocks.append({
                        'object': 'block',
                        'type': block_type,
                        block_type: {'rich_text': current_rich_texts}
                    })
                    current_rich_texts = []
                    current_length = 0
                
                current_rich_texts.append(rt)
                current_length += rt_length
            
            # 남은 것 추가
            if current_rich_texts:
                blocks.append({
                    'object': 'block',
                    'type': block_type,
                    block_type: {'rich_text': current_rich_texts}
                })
        
        return blocks
    
    children = []
    parts = re.split(r'(\{\{IMAGE_PLACEHOLDER:[^}]+\}\})', content)
    
    for part in parts:
        if m := re.match(r'\{\{IMAGE_PLACEHOLDER:([^}]+)\}\}', part):
            file_path = m.group(1)
            if url := uploaded_map.get(file_path):
                children.append({
                    'object': 'block', 
                    'type': 'embed',
                    'embed': {'url': url}
                })
            continue
        
        lines = [l.strip() for l in part.split('\n')]
        i = 0
        while i < len(lines):
            line = lines[i]
            if not line:
                i += 1
                continue
            
            # 테이블
            if line.startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                
                # 테이블 파싱
                if len(table_lines) >= 2:
                    # 헤더와 구분선 제거하고 데이터 행만 추출
                    header_row = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
                    data_rows = []
                    
                    for row in table_lines[2:]:  # 첫 줄은 헤더, 둘째 줄은 구분선
                        cells = [cell.strip() for cell in row.split('|')[1:-1]]
                        if cells:
                            data_rows.append(cells)
                    
                    # Notion 테이블 블록 생성
                    if data_rows:
                        table_width = len(header_row)
                        
                        # 모든 행의 셀 개수를 table_width에 맞춤
                        def normalize_row(row, width):
                            """행의 셀 개수를 width에 맞춤 (부족하면 빈 셀 추가, 초과하면 자름)"""
                            if len(row) < width:
                                return row + [''] * (width - len(row))
                            elif len(row) > width:
                                return row[:width]
                            return row
                        
                        header_row = normalize_row(header_row, table_width)
                        data_rows = [normalize_row(row, table_width) for row in data_rows]
                        
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
                        
                        # 헤더 행 (마크다운 파싱 적용)
                        header_cells = [parse_rich_text(cell) for cell in header_row]
                        table_block['table']['children'].append({
                            'object': 'block',
                            'type': 'table_row',
                            'table_row': {'cells': header_cells}
                        })
                        
                        # 데이터 행들 (마크다운 파싱 적용)
                        for row in data_rows:
                            row_cells = [parse_rich_text(cell) for cell in row]
                            table_block['table']['children'].append({
                                'object': 'block',
                                'type': 'table_row',
                                'table_row': {'cells': row_cells}
                            })
                        
                        children.append(table_block)
                    else:
                        # 파싱 실패시 코드 블록으로 대체
                        children.append({
                            'object': 'block', 'type': 'code',
                            'code': {'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table_lines)}}], 'language': 'plain text'}
                        })
                else:
                    # 테이블이 너무 짧으면 코드 블록
                    children.append({
                        'object': 'block', 'type': 'code',
                        'code': {'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table_lines)}}], 'language': 'plain text'}
                    })
                continue
            
            # 마크다운 파싱
            if line.startswith('### '):
                children.extend(make_block('heading_3', line[4:]))
            elif line.startswith('## '):
                children.extend(make_block('heading_2', line[3:]))
            elif line.startswith('# '):
                children.extend(make_block('heading_1', line[2:]))
            elif re.match(r'^\s*\d+\.\s', line):
                # Numbered list with potential nested bullets
                text = re.sub(r'^\s*\d+\.\s+', '', line)
                blocks = make_block('numbered_list_item', text)
                
                # Look ahead for bulleted items to nest as children
                nested_bullets = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if not next_line:
                        j += 1
                        continue
                    if re.match(r'^\s*[-*]\s', next_line):
                        # This is a bullet to nest
                        bullet_text = re.sub(r'^\s*[-*]\s+', '', next_line)
                        nested_bullets.extend(make_block('bulleted_list_item', bullet_text))
                        j += 1
                    else:
                        # Stop at non-bullet line
                        break
                
                # Add nested bullets as children if any
                if nested_bullets:
                    for block in blocks:
                        if block['type'] == 'numbered_list_item':
                            block['numbered_list_item']['children'] = nested_bullets
                    i = j - 1  # Skip processed bullets
                
                children.extend(blocks)
            elif re.match(r'^\s*[-*]\s', line):
                # Standalone bullet list (not nested under numbered item)
                text = re.sub(r'^\s*[-*]\s+', '', line)
                children.extend(make_block('bulleted_list_item', text))
            else:
                children.extend(make_block('paragraph', line))
            
            i += 1
    
    return children


def upload_to_notion(title: str, content: str, uploaded_map: dict[str, str]) -> Dict[str, str]:
    """Notion에 페이지 업로드 (기존 페이지에 추가)"""
    try:
        database_id = os.environ.get('NOTION_DATABASE_ID')
        api_key = os.environ.get('NOTION_API_KEY')
        
        if not database_id or not api_key:
            return {"status": "error", "message": "환경변수 설정 필요"}
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Notion-Version': '2025-09-03'
        }
        
        # 1. 기존 페이지 찾기 (같은 제목으로)
        search_data = {
            'query': title,
            'filter': {'property': 'object', 'value': 'page'}
        }
        
        search_response = requests.post('https://api.notion.com/v1/search', headers=headers, json=search_data)
        
        if search_response.status_code == 200:
            pages = search_response.json().get('results', [])
            existing_page = None
            
            # 같은 제목의 페이지 찾기
            for page in pages:
                if page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('text', {}).get('content') == title:
                    existing_page = page
                    break
            
            # 기존 페이지 찾기 기능 임시 비활성화 (이미지 표시 문제)
            if False and existing_page:
                # 2. 기존 페이지에 블록 추가
                page_id = existing_page['id']
                all_blocks = create_notion_blocks(content, uploaded_map)
                
                # 블록을 100개씩 나눠서 추가
                batch_size = 100
                for i in range(0, len(all_blocks), batch_size):
                    batch = all_blocks[i:i + batch_size]
                    batch_response = requests.patch(
                        f'https://api.notion.com/v1/blocks/{page_id}/children',
                        headers=headers,
                        json={'children': batch}
                    )
                    if batch_response.status_code != 200:
                        error_data = batch_response.json()
                        print(f"⚠️ 블록 추가 부분 실패: {error_data}")
                
                page_url = existing_page['url']
                print(f"✅ 기존 페이지에 추가 완료: {page_url}")
                return {"status": "success", "url": page_url}
        
        # 3. 페이지 생성 (children 포함)
        all_blocks = create_notion_blocks(content, uploaded_map)
        data = {
            'parent': {'page_id': database_id},
            'properties': {'title': {'title': [{'text': {'content': title}}]}},
            'children': all_blocks[:100]  # 최대 100개만
        }
        
        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        
        if response.status_code == 200:
            page_id = response.json()['id']
            page_url = response.json()['url']
            
            # 100개 이상이면 나머지 블록 추가
            if len(all_blocks) > 100:
                batch_size = 100
                for i in range(100, len(all_blocks), batch_size):
                    batch = all_blocks[i:i + batch_size]
                    batch_response = requests.patch(
                        f'https://api.notion.com/v1/blocks/{page_id}/children',
                        headers=headers,
                        json={'children': batch}
                    )
                    if batch_response.status_code != 200:
                        error_data = batch_response.json()
                        print(f"⚠️ 블록 추가 실패: {error_data}")
            
            print(f"✅ 새 페이지 생성 완료: {page_url}")
            return {"status": "success", "url": page_url}
        else:
            error_data = response.json()
            print(f"❌ 업로드 실패: {response.status_code} - {error_data}")
            return {"status": "error", "message": f"업로드 실패: {error_data.get('message', 'Unknown')}"}
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {"status": "error", "message": str(e)}

