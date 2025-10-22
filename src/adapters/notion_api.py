"""Notion API 어댑터 - Notion 페이지 생성 및 블록 관리"""

import os
import re
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv(override=True)


def create_notion_blocks(content: str, uploaded_map: dict[str, str]) -> list[dict]:
    """간단한 마크다운 파서로 Notion 블록 생성"""
    def make_block(block_type: str, text: str) -> list[dict]:
        """텍스트가 2000자를 초과하면 여러 블록으로 분할"""
        blocks = []
        # 2000자씩 분할
        while text:
            chunk = text[:2000]
            text = text[2000:]
            blocks.append({
                'object': 'block', 
                'type': block_type,
                block_type: {'rich_text': [{'type': 'text', 'text': {'content': chunk}}]}
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
                        
                        # 헤더 행
                        header_cells = [{'type': 'text', 'text': {'content': cell}} for cell in header_row]
                        table_block['table']['children'].append({
                            'object': 'block',
                            'type': 'table_row',
                            'table_row': {'cells': [[cell] for cell in header_cells]}
                        })
                        
                        # 데이터 행들
                        for row in data_rows:
                            row_cells = [{'type': 'text', 'text': {'content': cell}} for cell in row]
                            table_block['table']['children'].append({
                                'object': 'block',
                                'type': 'table_row',
                                'table_row': {'cells': [[cell] for cell in row_cells]}
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
            elif line.startswith(('- ', '* ')):
                children.extend(make_block('bulleted_list_item', line[2:]))
            elif re.match(r'^\d+\.\s', line):
                children.extend(make_block('numbered_list_item', re.sub(r'^\d+\.\s+', '', line)))
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

