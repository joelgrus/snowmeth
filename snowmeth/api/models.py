"""Pydantic models for API requests and responses."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class StoryCreateRequest(BaseModel):
    """Request model for creating a new story."""
    slug: str = Field(..., description="URL-friendly story identifier")
    story_idea: str = Field(..., description="The core story concept")


class StoryResponse(BaseModel):
    """Response model for story data."""
    story_id: str = Field(..., description="Unique story identifier (UUID)")
    slug: str = Field(..., description="URL-friendly story identifier")
    story_idea: str = Field(..., description="The core story concept")
    current_step: int = Field(..., description="Current step in the Snowflake Method")
    created_at: Optional[str] = Field(None, description="ISO timestamp of creation")
    
    class Config:
        orm_mode = True


class StoryDetailResponse(StoryResponse):
    """Detailed story response including steps."""
    steps: Dict[str, str] = Field(default_factory=dict, description="Story content by step")


class StoryListResponse(BaseModel):
    """Response model for listing stories."""
    stories: List[StoryResponse]
    total: int


class RefineRequest(BaseModel):
    """Request model for refining content."""
    instructions: str = Field(..., description="Specific instructions for refinement")


class AnalysisResponse(BaseModel):
    """Response model for story analysis."""
    overall_assessment: Dict[str, Any]
    recommendations: Dict[str, List[str]]
    analysis_timestamp: str


class SceneImproveRequest(BaseModel):
    """Request model for improving scenes."""
    scene_numbers: List[int] = Field(..., description="Scene numbers to improve")
    auto_accept: bool = Field(False, description="Automatically accept improvements")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    
    
class TaskResponse(BaseModel):
    """Response for async task creation."""
    task_id: str
    status: str = "pending"
    message: str
    
    
class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: str  # pending, processing, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    progress: Optional[float] = None  # 0.0 to 1.0