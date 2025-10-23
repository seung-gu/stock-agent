"""Notion API adapter - Page creation and block management"""

import os
import requests
from typing import Dict
from dotenv import load_dotenv

from src.adapters.markdown_to_notion import create_notion_blocks

load_dotenv(override=True)


def _get_api_headers() -> Dict[str, str]:
    """Get Notion API headers"""
    api_key = os.environ.get('NOTION_API_KEY')
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Notion-Version': '2025-09-03'
    }


def _create_page(title: str, blocks: list, database_id: str, headers: Dict[str, str]) -> Dict[str, str]:
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
    page_url = response.json()['url']
    
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
    return {"status": "success", "url": page_url}


def upload_to_notion(title: str, content: str, uploaded_map: dict[str, str]) -> Dict[str, str]:
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

