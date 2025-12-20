"""Notion API adapter - Page creation and block management"""

import os
import requests
from dotenv import load_dotenv

from src.adapters.markdown_to_notion import create_notion_blocks

load_dotenv(override=True)


def _get_api_headers() -> dict[str, str]:
    """Get Notion API headers"""
    api_key = os.environ.get('NOTION_API_KEY')
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2025-09-03'
    }


def _create_page(title: str, blocks: list, database_id: str, headers: dict[str, str]) -> dict[str, str]:
    """Create new Notion page"""
    # Create page with first 100 blocks
    data = {
        'parent': {'page_id': database_id},
        'properties': {'title': {'title': [{'text': {'content': title}}]}},
        'children': blocks[:100]
    }
    
    response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
    
    if response.status_code != 200:
        error_data = response.json()
        print(f"❌ Upload failed: {response.status_code} - {error_data}")
        return {"status": "error", "message": f"Upload failed: {error_data.get('message', 'Unknown')}"}
    
    page_id = response.json()['id']
    page_url = response.json()['public_url'] if response.json().get('public_url') else response.json()['url']
    
    # Add remaining blocks if more than 100 (Notion API limit)
    if len(blocks) > 100:
        batch_size = 100
        for i in range(100, len(blocks), batch_size):
            batch = blocks[i:i + batch_size]
            batch_response = requests.patch(
                f'https://api.notion.com/v1/blocks/{page_id}/children',
                headers=headers,
                json={'children': batch}
            )
            if batch_response.status_code != 200:
                error_data = batch_response.json()
                print(f"⚠️ Block addition failed: {error_data}")
    
    print(f"✅ New page created: {page_url}")
    return {"status": "success", "url": page_url, "page_id": page_id}


def create_child_page(parent_page_id: str, title: str, content: str, uploaded_map: dict[str, str]) -> dict[str, str]:
    """Create a child page under a parent page"""
    try:
        headers = _get_api_headers()
        blocks = create_notion_blocks(content, uploaded_map)
        
        # Create child page
        data = {
            'parent': {'page_id': parent_page_id},
            'properties': {'title': {'title': [{'text': {'content': title}}]}},
            'children': blocks[:100]
        }
        
        response = requests.post('https://api.notion.com/v1/pages', headers=headers, json=data)
        
        if response.status_code != 200:
            error_data = response.json()
            print(f"❌ Child page creation failed: {response.status_code} - {error_data}")
            return {"status": "error", "message": f"Child page creation failed: {error_data.get('message', 'Unknown')}"}
        
        page_id = response.json()['id']
        page_url = response.json()['url']
        
        # Add remaining blocks if more than 100
        if len(blocks) > 100:
            batch_size = 100
            for i in range(100, len(blocks), batch_size):
                batch = blocks[i:i + batch_size]
                batch_response = requests.patch(
                    f'https://api.notion.com/v1/blocks/{page_id}/children',
                    headers=headers,
                    json={'children': batch}
                )
                if batch_response.status_code != 200:
                    error_data = batch_response.json()
                    print(f"⚠️ Block addition failed: {error_data}")
        
        print(f"✅ Child page created: {page_url}")
        return {"status": "success", "url": page_url, "page_id": page_id}
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}


def add_link_to_page(parent_page_id: str, child_page_id: str, headers: dict[str, str]) -> None:
    """Add a link_to_page block to parent page"""
    link_block = {
        'object': 'block',
        'type': 'link_to_page',
        'link_to_page': {'type': 'page_id', 'page_id': child_page_id}
    }
    
    response = requests.patch(
        f'https://api.notion.com/v1/blocks/{parent_page_id}/children',
        headers=headers,
        json={'children': [link_block]}
    )
    
    if response.status_code != 200:
        error_data = response.json()
        print(f"⚠️ Link addition failed: {error_data}")


def upload_to_notion(title: str, content: str, uploaded_map: dict[str, str]) -> dict[str, str]:
    """Upload content to Notion as a new page"""
    try:
        database_id = os.environ.get('NOTION_DATABASE_ID')
        api_key = os.environ.get('NOTION_API_KEY')
        
        if not database_id or not api_key:
            return {"status": "error", "message": "Environment variables not set"}
        
        headers = _get_api_headers()
        blocks = create_notion_blocks(content, uploaded_map)
        
        return _create_page(title, blocks, database_id, headers)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

