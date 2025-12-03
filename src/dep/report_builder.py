"""Report building utilities for Notion"""

from src.adapters.notion_api import upload_to_notion, create_child_page
from src.services.image_service import find_local_images
from src.types.analysis_report import AnalysisReport


def upload_report_with_children(
    title: str,
    date: str,
    summary: str,
    child_pages: list[tuple[str, str]],
    uploaded_map: dict[str, str]
) -> dict[str, str]:
    """
    Upload a report with parent page and child pages.
    
    Args:
        title: Report title
        date: Report date
        summary: Executive summary
        child_pages: List of (child_title, child_content) tuples
        uploaded_map: Map of local image paths to uploaded URLs
        
    Returns:
        Dict with status, parent page info, and child_page_ids mapping
    """
    try:
        # Create parent page - Agent-generated title and summary
        parent_content = f"""# {title}

*{date}*

{summary}
"""
        
        # Upload parent page
        parent_result = upload_to_notion(title, parent_content, {})
        
        if parent_result['status'] != 'success':
            print(f"❌ Parent page creation failed: {parent_result}")
            return parent_result
        
        parent_page_id = parent_result['page_id']
        print(f"✅ Parent page created: {parent_result['url']}")
        
        # Create child pages and store their IDs
        child_page_ids = {}
        for child_title, child_content in child_pages:
            # Each child page content is processed independently
            # find_local_images processes images in-place and returns processed content
            child_processed, _, _ = find_local_images(child_content)
            child_result = create_child_page(parent_page_id, child_title, child_processed, uploaded_map)
            if child_result['status'] == 'success':
                child_page_ids[child_title] = child_result['page_id']
        
        print("📝 Report upload complete!")
        parent_result['child_page_ids'] = child_page_ids
        return parent_result
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

