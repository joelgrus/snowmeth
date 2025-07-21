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


@app.post("/api/stories/{story_id}/generate_paragraph_summary", response_model=StoryDetailResponse)
async def generate_paragraph_summary(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Generate Step 2: One paragraph summary from the sentence."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        # Ensure we have step 1 content
        sentence = story.get_step_content(1)
        if not sentence:
            raise HTTPException(status_code=400, detail="Step 1 sentence is required to generate paragraph")
        
        # Generate paragraph using workflow
        workflow = SnowflakeWorkflow()
        paragraph = workflow.expand_to_paragraph(story)
        
        # Save the generated content to step 2
        story.set_step_content(2, paragraph)
        
        # If this is advancing to step 2, update current_step
        current_step = story.get_current_step()
        if current_step < 2:
            story.data["current_step"] = 2
        
        await storage.save_story(story)
        
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


@app.post("/api/stories/{story_id}/generate_characters", response_model=StoryDetailResponse)
async def generate_characters(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Generate Step 3: Main characters list."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        # Ensure we have previous steps
        if not story.get_step_content(1) or not story.get_step_content(2):
            raise HTTPException(status_code=400, detail="Steps 1 and 2 are required to generate characters")
        
        # Generate characters using workflow
        workflow = SnowflakeWorkflow()
        characters_content = workflow.extract_characters(story)
        
        # Save the generated content to step 3
        story.set_step_content(3, characters_content)
        
        # If this is advancing to step 3, update current_step
        current_step = story.get_current_step()
        if current_step < 3:
            story.data["current_step"] = 3
        
        await storage.save_story(story)
        
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


@app.post("/api/stories/{story_id}/generate_plot_structure", response_model=StoryDetailResponse)
async def generate_plot_structure(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Generate Step 4: Story structure/plot summary."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        # Ensure we have previous steps
        if not story.get_step_content(1) or not story.get_step_content(2) or not story.get_step_content(3):
            raise HTTPException(status_code=400, detail="Steps 1-3 are required to generate plot structure")
        
        # Generate plot structure using workflow
        workflow = SnowflakeWorkflow()
        plot_content = workflow.expand_to_plot(story)
        
        # Save the generated content to step 4
        story.set_step_content(4, plot_content)
        
        # If this is advancing to step 4, update current_step
        current_step = story.get_current_step()
        if current_step < 4:
            story.data["current_step"] = 4
        
        await storage.save_story(story)
        
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


@app.post("/api/stories/{story_id}/generate_character_synopses", response_model=StoryDetailResponse)
async def generate_character_synopses(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Generate Step 5: Character synopses."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        # Ensure we have previous steps
        if not all(story.get_step_content(i) for i in range(1, 5)):
            raise HTTPException(status_code=400, detail="Steps 1-4 are required to generate character synopses")
        
        # Generate character synopses using workflow
        workflow = SnowflakeWorkflow()
        synopses_content = workflow.generate_character_synopses(story)
        
        # Save the generated content to step 5
        story.set_step_content(5, synopses_content)
        
        # If this is advancing to step 5, update current_step
        current_step = story.get_current_step()
        if current_step < 5:
            story.data["current_step"] = 5
        
        await storage.save_story(story)
        
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


@app.post("/api/stories/{story_id}/generate_detailed_synopsis", response_model=StoryDetailResponse)
async def generate_detailed_synopsis(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Generate Step 6: Detailed story synopsis."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        # Ensure we have previous steps
        if not all(story.get_step_content(i) for i in range(1, 6)):
            raise HTTPException(status_code=400, detail="Steps 1-5 are required to generate detailed synopsis")
        
        # Generate detailed synopsis using workflow
        workflow = SnowflakeWorkflow()
        synopsis_content = workflow.expand_to_detailed_plot(story)
        
        # Save the generated content to step 6
        story.set_step_content(6, synopsis_content)
        
        # If this is advancing to step 6, update current_step
        current_step = story.get_current_step()
        if current_step < 6:
            story.data["current_step"] = 6
        
        await storage.save_story(story)
        
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


@app.post("/api/stories/{story_id}/next", response_model=StoryDetailResponse)
async def advance_story(
    story_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Advance to the next step (without generating content)."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)
        
        current_step = story.get_current_step()
        if current_step < 10:
            new_step = current_step + 1
            story.data["current_step"] = new_step
            await storage.save_story(story)
        
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