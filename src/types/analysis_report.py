from pydantic import BaseModel, Field


class IndicatorScore(BaseModel):
    """Individual indicator score model"""
    agent: str = Field(description="Agent name (e.g. 'S&P 500', 'VIX', 'MarketBreadth')")
    indicator: str = Field(description="Indicator name (e.g. 'RSI(14)', 'Disparity(200)', 'BullBear')")
    value: int | float = Field(ge=1, le=5, description="Score between 1-5")
    
    class Config:
        extra = "forbid"


class AnalysisReport(BaseModel):
    """Comprehensive analysis report data model"""
    
    # Basic Information
    title: str = Field(description="Specific, descriptive title for the analysis report", default="")
    summary: str = Field(description="Executive summary of the analysis findings and key insights", default="")
    content: str = Field(description="Detailed analysis content including data, charts, and comprehensive insights", default="")
    
    # Optional scoring data
    score: list[IndicatorScore] = Field(
        default_factory=list,
        description="List of indicator scores. Examples: [], [{'indicator':'BullBear','value':3}], [{'indicator':'RSI(14)','value':4},{'indicator':'Disparity(200)','value':3}]"
    )
    
    class Config:
        extra = "forbid"


