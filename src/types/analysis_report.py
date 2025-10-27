from pydantic import BaseModel, Field

class AnalysisReport(BaseModel):
    """Comprehensive analysis report data model"""
    
    # Basic Information
    title: str = Field(description="Specific, descriptive title for the analysis report", default="")
    summary: str = Field(description="Executive summary of the analysis findings and key insights", default="")
    content: str = Field(description="Detailed analysis content including data, charts, and comprehensive insights", default="")
    
    class Config:
        extra = "forbid"


