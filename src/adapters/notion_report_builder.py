"""Notion report builder with hierarchical structure support"""

from src.adapters.notion_api import upload_to_notion, create_child_page
from src.services.image_service import find_local_images, upload_images_to_cloudflare
from src.types.analysis_report import AnalysisReport


class NotionReportBuilder:
    """
    Builder for creating hierarchical Notion report structures.
    
    Usage:
        builder = NotionReportBuilder()
        builder.add_page(report1)
        builder.add_page(report2).add_children([sub1, sub2])
        result = builder.upload(title, date, summary, uploaded_map)
    """
    
    def __init__(self):
        self._pages = []
    
    def add_page(self, report: AnalysisReport):
        """
        Add a 1st level page.
        
        Args:
            report: AnalysisReport object
            
        Returns:
            self (for method chaining)
        """
        self._pages.append({
            'report': report,
            'children': []
        })
        return self
    
    def add_children(self, children_reports: list[AnalysisReport]):
        """
        Add children pages (2nd level) to the last added page.
        
        Args:
            children_reports: List of child AnalysisReport objects
            
        Returns:
            self (for method chaining)
        """
        if self._pages:
            self._pages[-1]['children'] = children_reports
        return self
    
    def upload(self, title: str, date: str, summary: str) -> dict:
        """
        Upload the built structure to Notion with automatic image processing.
        
        Args:
            title: Report title
            date: Report date
            summary: Executive summary
            
        Returns:
            Upload result dict with status, url, page_id, and child_page_ids
        """
        try:
            uploaded_map = self._process_all_images(summary)
            parent_result = self._create_parent_page(title, date, summary, uploaded_map)
            
            if parent_result['status'] != 'success':
                return parent_result
            
            child_page_ids = self._create_child_pages(parent_result['page_id'], uploaded_map)
            
            parent_result['child_page_ids'] = child_page_ids
            print("📝 Report upload complete!")
            return parent_result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _process_all_images(self, summary: str) -> dict:
        """Collect all content and process images."""
        all_contents = [summary]
        for page_item in self._pages:
            all_contents.append(page_item['report'].content)
            for child_report in page_item['children']:
                all_contents.append(child_report.content)
        
        _, image_files, _ = find_local_images(" ".join(all_contents))
        return upload_images_to_cloudflare(image_files) if image_files else {}
    
    def _create_parent_page(self, title: str, date: str, summary: str, uploaded_map: dict) -> dict:
        """Create parent page."""
        parent_content = f"""# {title}

*{date}*

{summary}
"""
        parent_result = upload_to_notion(title, parent_content, uploaded_map)
        
        if parent_result['status'] == 'success':
            print(f"✅ Parent page created: {parent_result['url']}")
        else:
            print(f"❌ Parent page creation failed: {parent_result}")
        
        return parent_result
    
    def _create_child_pages(self, parent_page_id: str, uploaded_map: dict) -> dict:
        """Create 1st and 2nd level child pages."""
        child_page_ids = {}
        
        for page_item in self._pages:
            report = page_item['report']
            
            # Create 1st level page
            processed, _, _ = find_local_images(report.content)
            child_result = create_child_page(parent_page_id, report.title, processed, uploaded_map)
            
            if child_result['status'] == 'success':
                child_page_ids[report.title] = child_result['page_id']
                
                # Create 2nd level pages if children exist
                if page_item['children']:
                    self._create_sub_pages(child_result['page_id'], page_item['children'], uploaded_map, report.title)
        
        return child_page_ids
    
    def _create_sub_pages(self, parent_page_id: str, children: list, uploaded_map: dict, parent_title: str):
        """Create 2nd level pages under a parent."""
        print(f"📂 Creating {len(children)} sub-pages under '{parent_title}'...")
        
        for sub_report in children:
            sub_processed, _, _ = find_local_images(sub_report.content)
            create_child_page(parent_page_id, sub_report.title, sub_processed, uploaded_map)

