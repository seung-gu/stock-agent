import os
import requests
import base64
from typing import Dict
from agents import Agent, ModelSettings, function_tool


def find_local_images(content: str) -> tuple[str, list[tuple[str, str]], dict[str, str]]:
    """로컬 이미지 파일 찾기 - (processed_content, image_files, image_map) 반환"""
    import re, glob, os as os_module
    
    processed_content = content
    image_files = []
    image_map = {}  # {file_path: alt_text} 매핑
    
    # 1. 이미지 링크 파싱: ![alt](sandbox:/path)
    image_pattern = r'!\[([^\]]*)\]\(sandbox:([^)]+)\)'
    image_matches = re.findall(image_pattern, content)
    
    for alt_text, file_path in image_matches:
        if os_module.path.exists(file_path):
            image_files.append(file_path)
            image_map[file_path] = alt_text
            processed_content = processed_content.replace(
                f'![{alt_text}](sandbox:{file_path})', 
                f'{{{{IMAGE_PLACEHOLDER:{file_path}}}}}'
            )
    
    # 2. 일반 링크 파싱: [텍스트](sandbox:/path)
    link_pattern = r'\[([^\]]+)\]\(sandbox:([^)]+)\)'
    link_matches = re.findall(link_pattern, content)
    
    for link_text, file_path in link_matches:
        if os_module.path.exists(file_path):
            if file_path not in image_files:
                image_files.append(file_path)
            image_map[file_path] = link_text
            processed_content = processed_content.replace(
                f'[{link_text}](sandbox:{file_path})', 
                f'{{{{IMAGE_PLACEHOLDER:{file_path}}}}}'
            )
    
    # 차트 디렉토리에서 파일 찾기
    for pattern in ['/tmp/market_charts_*', '/var/folders/*/T/market_charts_*']:
        dirs = glob.glob(pattern)
        if dirs:
            latest_dir = max(dirs, key=os_module.path.getmtime)
            chart_files = glob.glob(f'{latest_dir}/*.png')
            for chart_file in chart_files:
                if chart_file not in image_files:
                    image_files.append(chart_file)
            break
    
    return processed_content, image_files, image_map


def upload_images_to_cloudflare(image_files: list[str]) -> dict[str, str]:
    """R2에 이미지 업로드 - {file_path: url} 반환"""
    from PIL import Image
    import io, boto3, time
    from dotenv import load_dotenv
    
    load_dotenv(override=True)
    
    uploaded_map = {}
    r2_client = boto3.client('s3',
        endpoint_url=f'https://{os.environ["R2_ACCOUNT_ID"]}.r2.cloudflarestorage.com',
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        region_name='auto'
    )
    
    for chart_file in image_files[:6]:
        try:
            print(f"🔄 R2 업로드 시작: {chart_file}")
            filename = os.path.basename(chart_file)
            with Image.open(chart_file) as img:
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.convert('RGB').save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                
                object_key = f"charts/{filename.replace('.png', f'_{int(time.time())}.jpg')}"
                print(f"📤 R2 업로드 중: {object_key}")
                r2_client.upload_fileobj(buffer, os.environ['R2_BUCKET_NAME'], object_key,
                    ExtraArgs={'ContentType': 'image/jpeg'})
                
                image_url = f"https://pub-8ab005469c4042798a7550efc290ac49.r2.dev/{object_key}"
                uploaded_map[chart_file] = image_url
                print(f"✅ R2 업로드 성공: {filename} -> {image_url}")
        except Exception as e:
            print(f"❌ R2 업로드 실패: {chart_file} - {e}")
    
    return uploaded_map


def create_notion_blocks(content: str, uploaded_map: dict[str, str]) -> list[dict]:
    """간단한 마크다운 파서로 Notion 블록 생성"""
    import re
    
    def make_block(block_type: str, text: str) -> dict:
        return {
            'object': 'block', 
            'type': block_type,
            block_type: {'rich_text': [{'type': 'text', 'text': {'content': text[:2000]}}]}
        }
    
    children = []
    parts = re.split(r'(\{\{IMAGE_PLACEHOLDER:[^}]+\}\})', content)
    
    for part in parts:
        if m := re.match(r'\{\{IMAGE_PLACEHOLDER:([^}]+)\}\}', part):
            if url := uploaded_map.get(m.group(1)):
                children.append({
                    'object': 'block', 'type': 'image',
                    'image': {'type': 'external', 'external': {'url': url}}
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
                table = []
                while i < len(lines) and lines[i].startswith('|'):
                    table.append(lines[i])
                    i += 1
                children.append({
                    'object': 'block', 'type': 'code',
                    'code': {'rich_text': [{'type': 'text', 'text': {'content': '\n'.join(table)[:2000]}}], 'language': 'plain text'}
                })
                continue
            
            # 마크다운 파싱
            if line.startswith('### '):
                children.append(make_block('heading_3', line[4:]))
            elif line.startswith('## '):
                children.append(make_block('heading_2', line[3:]))
            elif line.startswith('# '):
                children.append(make_block('heading_1', line[2:]))
            elif line.startswith(('- ', '* ')):
                children.append(make_block('bulleted_list_item', line[2:]))
            elif re.match(r'^\d+\.\s', line):
                children.append(make_block('numbered_list_item', re.sub(r'^\d+\.\s+', '', line)))
            else:
                children.append(make_block('paragraph', line))
            
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
            
            if existing_page:
                # 2. 기존 페이지에 블록 추가
                page_id = existing_page['id']
                blocks = create_notion_blocks(content, uploaded_map)
                
                # 블록들을 기존 페이지에 추가
                for block in blocks:
                    block_response = requests.patch(
                        f'https://api.notion.com/v1/blocks/{page_id}/children',
                        headers=headers,
                        json={'children': [block]}
                    )
                
                page_url = existing_page['url']
                print(f"✅ 기존 페이지에 추가 완료: {page_url}")
                return {"status": "success", "url": page_url}
        
        # 3. 기존 페이지가 없으면 새로 생성
        data = {
            'parent': {'page_id': database_id},
            'properties': {'title': {'title': [{'text': {'content': title}}]}},
            'children': create_notion_blocks(content, uploaded_map)
        }
        
        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        
        if response.status_code == 200:
            page_url = response.json()['url']
            print(f"✅ 새 페이지 생성 완료: {page_url}")
            return {"status": "success", "url": page_url}
        else:
            error_data = response.json()
            print(f"❌ 업로드 실패: {response.status_code} - {error_data}")
            return {"status": "error", "message": f"업로드 실패: {error_data.get('message', 'Unknown')}"}
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {"status": "error", "message": str(e)}


@function_tool
def post_to_notion(title: str, content: str) -> Dict[str, str]:
    """Notion에 자동 포스트"""
    try:
        processed_content, image_files, image_map = find_local_images(content)
        uploaded_map = upload_images_to_cloudflare(image_files) if image_files else {}
        return upload_to_notion(title, processed_content, uploaded_map)
    except Exception as e:
        print(f"❌ 오류: {e}")
        return {"status": "error", "message": str(e)}


INSTRUCTIONS = """Notion 자동 업로드 에이전트입니다.

받은 리포트를 Notion에 자동으로 업로드합니다.
- 제목과 내용을 정리해서 Notion 페이지로 생성
- API를 통해 자동으로 업로드
- 수동 작업 없이 완전 자동화"""

notion_agent = Agent(
    name="Notion Agent",
    instructions=INSTRUCTIONS,
    tools=[post_to_notion],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required")
)