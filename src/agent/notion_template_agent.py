"""Simple Notion page structure generator"""

from agents import Agent, Runner
from src.config import REPORT_LANGUAGE
from pydantic import BaseModel, Field
from typing import List


class ChildPage(BaseModel):
    """Child page structure"""
    title: str = Field(description="Child page title")
    content: str = Field(description="Child page content")

class NotionTemplate(BaseModel):
    """Notion page structure data model"""
    title: str = Field(description="Main page title")
    summary: str = Field(description="Page summary")
    child_pages: List[ChildPage] = Field(description="List of child pages")
    
    class Config:
        extra = "forbid"


class NotionTemplateAgent:
    """AI-powered Notion page template generator"""
    
    def __init__(self):
        """Initialize Notion template agent"""
        self.agent = Agent(
            name="notion_template_agent",
            model="gpt-4o-mini",
            instructions=f"""Generate Notion page structure in {REPORT_LANGUAGE}.
            You will receive input in format: "Analysis types: Type1, Type2, ..., TypeN"
            Create exactly one child page for each analysis type listed.

            For child page titles, create appropriate titles for a market analysis report:
            - Convert technical class names to professional report titles
            - Make them suitable for financial/market analysis context
            - Use clear, descriptive titles that reflect the analysis content

            Return JSON with:
            - title: Main page title  
            - summary: Brief description
            - child_pages: List of {{"title": "Child title", "content": ""}}

            Set content to empty string for all child pages.""",
            output_type=NotionTemplate
        )
    
    async def generate_template(self, analysis_types: list[str]) -> NotionTemplate:
        """Generate Notion page template"""
        analysis_text = f"Analysis types: {', '.join(analysis_types)}"
        result = await Runner.run(self.agent, input=analysis_text)
        
        try:
            return result.final_output_as(NotionTemplate)
        except Exception as e:
            print(f"Error: {e}")
            return result.final_output
        