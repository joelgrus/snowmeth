"""Pydantic models for API requests and responses."""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class StoryCreateRequest(BaseModel):
    """Request model for creating a new story."""

    slug: str = Field(..., description="URL-friendly story identifier")
    story_idea: str = Field(..., description="The core story concept")


class RefineRequest(BaseModel):
    """Request model for refining step content."""

    step_number: int = Field(..., description="Step number to refine")
    instructions: str = Field(..., description="Instructions for how to refine the content")


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

    steps: Dict[str, str] = Field(
        default_factory=dict, description="Story content by step"
    )


class StoryListResponse(BaseModel):
    """Response model for listing stories."""

    stories: List[StoryResponse]
    total: int


# Unused models removed - only keeping models used by the simplified API
