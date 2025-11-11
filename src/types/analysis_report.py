from pydantic import BaseModel, Field


class AnalysisReport(BaseModel):
    """Comprehensive analysis report data model"""
    
    # Basic Information
    title: str = Field(description="Specific, descriptive title for the analysis report", default="")
    summary: str = Field(description="Executive summary of the analysis findings and key insights", default="")
    content: str = Field(description="Detailed analysis content including data, charts, and comprehensive insights", default="")
    
    # Optional scoring data
    score: str = Field(
        default="",
        description="Score for the analysis. Single indicator: '3'. Multiple indicators: 'RSI(14):4, Disparity(200):3, S5FI:2' (use TOOL/INDICATOR names, NOT periods)"
    )
    
    class Config:
        extra = "forbid"


