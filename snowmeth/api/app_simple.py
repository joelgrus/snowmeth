"""Simplified FastAPI application for Snowflake Method API."""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from .models import (
    StoryCreateRequest, StoryResponse, StoryDetailResponse, StoryListResponse,
    ErrorResponse
)
from .database import db_manager
from .async_storage import AsyncSQLiteStorage
from ..workflow import SnowflakeWorkflow
from ..exceptions import StoryNotFoundError

# Create FastAPI app
app = FastAPI(
    title="Snowflake Method API",
    description="Web API for the Snowflake Method writing assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await db_manager.create_tables()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with db_manager.async_session() as session:
        yield session


# Story Management Endpoints

@app.get("/api/stories", response_model=StoryListResponse)
async def list_stories(session: AsyncSession = Depends(get_db)):
    """List all stories."""
    storage = AsyncSQLiteStorage(session)
    stories = await storage.list_stories()
    
    return StoryListResponse(
        stories=[
            StoryResponse(
                story_id=story.story_id,
                slug=story.slug,
                story_idea=story.data.get("story_idea", ""),
                current_step=story.get_current_step(),
                created_at=story.data.get("created_at")
            )
            for story in stories
        ],
        total=len(stories)
    )


@app.post("/api/stories", response_model=StoryDetailResponse)
async def create_story(
    request: StoryCreateRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create a new story with initial sentence."""
    try:
        # Create story
        storage = AsyncSQLiteStorage(session)
        story = await storage.create_story(request.slug, request.story_idea)
        
        # Generate initial sentence
        workflow = SnowflakeWorkflow()
        sentence = workflow.generate_initial_sentence(request.story_idea)
        
        # Save sentence
        story.set_step_content(1, sentence)
        await storage.save_story(story)
        
        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={"1": sentence}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stories/{story_id}", response_model=StoryDetailResponse)
async def get_story(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get story details."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()}
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.delete("/api/stories/{story_id}")
async def delete_story(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Delete a story."""
    try:
        storage = AsyncSQLiteStorage(session)
        await storage.delete_story(story_id)
        return {"message": "Story deleted successfully"}
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Snowflake Method API",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)