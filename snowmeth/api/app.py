"""FastAPI application for Snowflake Method API."""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import asyncio
import uuid
import json

from .models import (
    StoryCreateRequest, StoryResponse, StoryDetailResponse, StoryListResponse,
    RefineRequest, AnalysisResponse, SceneImproveRequest, ErrorResponse,
    TaskResponse, TaskStatusResponse
)
from .database import db_manager, DbTask
from .async_storage import AsyncSQLiteStorage
from ..context import WebContext
from ..project import ProjectManager
from ..workflow import SnowflakeWorkflow, StepProgression, AnalysisWorkflow
from ..exceptions import SnowmethError, StoryNotFoundError

# Create FastAPI app
app = FastAPI(
    title="Snowflake Method API",
    description="Web API for the Snowflake Method writing assistant",
    version="1.0.0"
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task storage (in production, use Redis or similar)
background_tasks = {}


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await db_manager.create_tables()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async for session in db_manager.get_session():
        yield session


async def get_project_manager(
    story_id: Optional[str], 
    session: AsyncSession = Depends(get_db)
) -> ProjectManager:
    """Get project manager with web context."""
    storage = AsyncSQLiteStorage(session)
    context = WebContext(story_id=story_id) if story_id else None
    return ProjectManager(storage=storage, context=context)


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


@app.post("/api/stories", response_model=TaskResponse)
async def create_story(
    request: StoryCreateRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Create a new story (returns task for sentence generation)."""
    task_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(
        create_story_task,
        task_id,
        request.slug,
        request.story_idea
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Story creation started"
    )


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


# Story Progression Endpoints

@app.post("/api/stories/{story_id}/next", response_model=TaskResponse)
async def advance_story(
    story_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Advance to the next step in the Snowflake Method."""
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        advance_story_task,
        task_id,
        story_id
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Story advancement started"
    )


@app.post("/api/stories/{story_id}/refine", response_model=TaskResponse)
async def refine_story(
    story_id: str,
    request: RefineRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Refine the current step with specific instructions."""
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        refine_story_task,
        task_id,
        story_id,
        request.instructions
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Refinement started"
    )


# Analysis Endpoints

@app.post("/api/stories/{story_id}/analyze", response_model=TaskResponse)
async def analyze_story(
    story_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """Analyze story for consistency and completeness."""
    task_id = str(uuid.uuid4())
    
    background_tasks.add_task(
        analyze_story_task,
        task_id,
        story_id
    )
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
        message="Analysis started"
    )


# Task Status Endpoint

@app.get("/api/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get the status of an async task."""
    if task_id in background_tasks:
        return background_tasks[task_id]
    
    # Check database for completed tasks
    # (In production, implement proper task persistence)
    raise HTTPException(status_code=404, detail="Task not found")


# Background Task Functions

async def create_story_task(task_id: str, slug: str, story_idea: str):
    """Background task to create a story with initial sentence."""
    try:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="processing",
            progress=0.1
        )
        
        # Create story with new session
        async with db_manager.async_session() as session:
            storage = AsyncSQLiteStorage(session)
            story = await storage.create_story(slug, story_idea)
            
            background_tasks[task_id].progress = 0.3
            
            # Generate initial sentence
            workflow = SnowflakeWorkflow()
            sentence = workflow.generate_initial_sentence(story_idea)
            
            background_tasks[task_id].progress = 0.8
            
            # Save sentence
            story.set_step_content(1, sentence)
            await storage.save_story(story)
        
        # Complete
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="completed",
            result={
                "story_id": story.story_id,
                "sentence": sentence
            },
            progress=1.0
        )
        
    except Exception as e:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def advance_story_task(task_id: str, story_id: str):
    """Background task to advance story to next step."""
    try:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="processing",
            progress=0.1
        )
        
        # Load story with new session
        async with db_manager.async_session() as session:
            storage = AsyncSQLiteStorage(session)
            story = await storage.load_story(story_id)
            
            # Advance step
            workflow = SnowflakeWorkflow()
            progression = StepProgression(workflow)
            
            background_tasks[task_id].progress = 0.3
            
            success, message, content = progression.advance_step(story)
            
            if not success:
                raise Exception(message)
            
            background_tasks[task_id].progress = 0.8
            
            # Special handling for individual steps
            if content == "INDIVIDUAL_CHARACTERS":
                # Handle Step 7
                success, charts, errors = workflow.handle_character_charts_generation(story)
                if success and charts:
                    story.set_step_content(7, json.dumps(charts, indent=2))
                    await storage.save_story(story)
                    content = charts
            elif content == "INDIVIDUAL_SCENES":
                # Handle Step 9
                success, expansions, errors = workflow.handle_scene_expansions_generation(story)
                if success and expansions:
                    story.set_step_content(9, json.dumps(expansions, indent=2))
                    await storage.save_story(story)
                    content = expansions
            else:
                # Normal step progression
                progression.accept_step_content(story, content)
                await storage.save_story(story)
        
        # Complete
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="completed",
            result={
                "message": message,
                "content": content,
                "new_step": story.get_current_step()
            },
            progress=1.0
        )
        
    except Exception as e:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def refine_story_task(task_id: str, story_id: str, instructions: str):
    """Background task to refine current step."""
    try:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="processing",
            progress=0.1
        )
        
        # Load story with new session
        async with db_manager.async_session() as session:
            storage = AsyncSQLiteStorage(session)
            story = await storage.load_story(story_id)
            
            # Refine content
            workflow = SnowflakeWorkflow()
            
            background_tasks[task_id].progress = 0.3
            
            refined_content = workflow.refine_content(story, instructions)
            
            background_tasks[task_id].progress = 0.8
            
            # Save refined content
            current_step = story.get_current_step()
            story.set_step_content(current_step, refined_content)
            await storage.save_story(story)
        
        # Complete
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="completed",
            result={
                "refined_content": refined_content,
                "step": current_step
            },
            progress=1.0
        )
        
    except Exception as e:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


async def analyze_story_task(task_id: str, story_id: str):
    """Background task to analyze story."""
    try:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="processing",
            progress=0.1
        )
        
        # Load story with new session
        async with db_manager.async_session() as session:
            storage = AsyncSQLiteStorage(session)
            story = await storage.load_story(story_id)
            
            # Analyze
            workflow = SnowflakeWorkflow()
            analysis_workflow = AnalysisWorkflow(workflow)
            
            background_tasks[task_id].progress = 0.3
            
            analysis = analysis_workflow.analyze_story(story)
            
            background_tasks[task_id].progress = 0.9
            
            # Parse analysis
            import json
            analysis_data = json.loads(analysis)
        
        # Complete
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="completed",
            result=analysis_data,
            progress=1.0
        )
        
    except Exception as e:
        background_tasks[task_id] = TaskStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)