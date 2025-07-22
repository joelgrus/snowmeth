"""Simplified FastAPI application for Snowflake Method API."""

import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from .models import (
    StoryCreateRequest,
    StoryResponse,
    StoryDetailResponse,
    StoryListResponse,
    RefineRequest,
)
from .database import db_manager
from .sqlite_storage import AsyncSQLiteStorage
from ..workflow import SnowflakeWorkflow
from ..exceptions import StoryNotFoundError
from ..pdf_export import generate_story_pdf

# Create FastAPI app
app = FastAPI(
    title="Snowflake Method API",
    description="AI-powered writing assistant implementing Randy Ingermanson's Snowflake Method for novel planning",
    version="1.0.0",
    contact={
        "name": "Joel Grus",
        "url": "https://twitter.com/joelgrus",
    },
    license_info={
        "name": "Snowflake Method",
        "url": "https://www.advancedfictionwriting.com/articles/snowflake-method/",
    },
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
    try:
        await db_manager.create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        raise


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
                created_at=story.data.get("created_at"),
            )
            for story in stories
        ],
        total=len(stories),
    )


@app.post("/api/stories", response_model=StoryDetailResponse)
async def create_story(
    request: StoryCreateRequest, session: AsyncSession = Depends(get_db)
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
            steps={"1": sentence},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/stories/{story_id}", response_model=StoryDetailResponse)
async def get_story(story_id: str, session: AsyncSession = Depends(get_db)):
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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
            chapters=story.data.get("chapters", {}),
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.delete("/api/stories/{story_id}")
async def delete_story(story_id: str, session: AsyncSession = Depends(get_db)):
    """Delete a story."""
    try:
        storage = AsyncSQLiteStorage(session)
        await storage.delete_story(story_id)
        return {"message": "Story deleted successfully"}
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/rollback/{target_step}", response_model=StoryDetailResponse
)
async def rollback_story(
    story_id: str, target_step: int, session: AsyncSession = Depends(get_db)
):
    """Rollback story to a previous step and clear all future steps."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Validate target step
        if target_step < 1 or target_step >= story.get_current_step():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid rollback step. Must be between 1 and {story.get_current_step() - 1}",
            )

        # Clear all steps after the target step
        steps = story.data.get("steps", {})
        for step_num in list(steps.keys()):
            if int(step_num) > target_step:
                del steps[step_num]

        # Update current step
        story.data["current_step"] = target_step
        story.data["steps"] = steps

        # Save the updated story
        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post("/api/stories/{story_id}/refine", response_model=StoryDetailResponse)
async def refine_step_content(
    story_id: str, request: RefineRequest, session: AsyncSession = Depends(get_db)
):
    """Refine the content of a specific step with AI assistance."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Temporarily set the story's current step to the requested step for refinement
        original_step = story.get_current_step()
        story.data["current_step"] = request.step_number

        # Validate step has content
        step_content = story.get_step_content(request.step_number)
        if not step_content:
            story.data["current_step"] = original_step  # Restore original step
            raise HTTPException(
                status_code=400,
                detail=f"Step {request.step_number} has no content to refine",
            )

        # Refine using workflow
        workflow = SnowflakeWorkflow()
        refined_content = workflow.refine_content(story, request.instructions)

        # Restore original current step
        story.data["current_step"] = original_step

        # Save the refined content
        story.set_step_content(request.step_number, refined_content)

        # If refining an earlier step, clear all later steps and reset current_step
        if request.step_number < original_step:
            # Clear steps after the refined step
            steps = story.data.get("steps", {})
            for step_num in list(steps.keys()):
                if int(step_num) > request.step_number:
                    del steps[step_num]

            # Reset current step to the refined step
            story.data["current_step"] = request.step_number

        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_initial_sentence",
    response_model=StoryDetailResponse,
)
async def generate_initial_sentence(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Regenerate Step 1: Initial sentence from story idea."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Get story idea
        story_idea = story.data.get("story_idea", "")
        if not story_idea:
            raise HTTPException(
                status_code=400,
                detail="Story idea is required to regenerate sentence",
            )

        # Generate new sentence
        workflow = SnowflakeWorkflow()
        sentence = workflow.generate_initial_sentence(story_idea)

        # Save the new sentence to step 1
        story.set_step_content(1, sentence)

        # Clear any future steps since we're changing step 1
        current_step = story.get_current_step()
        if current_step > 1:
            steps = story.data.get("steps", {})
            for step_num in list(steps.keys()):
                if int(step_num) > 1:
                    del steps[step_num]
            story.data["current_step"] = 1
            story.data["steps"] = steps

        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_paragraph_summary",
    response_model=StoryDetailResponse,
)
async def generate_paragraph_summary(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 2: One paragraph summary from the sentence."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have step 1 content
        sentence = story.get_step_content(1)
        if not sentence:
            raise HTTPException(
                status_code=400,
                detail="Step 1 sentence is required to generate paragraph",
            )

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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_characters", response_model=StoryDetailResponse
)
async def generate_characters(story_id: str, session: AsyncSession = Depends(get_db)):
    """Generate Step 3: Main characters list."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have previous steps
        if not story.get_step_content(1) or not story.get_step_content(2):
            raise HTTPException(
                status_code=400,
                detail="Steps 1 and 2 are required to generate characters",
            )

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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_plot_structure",
    response_model=StoryDetailResponse,
)
async def generate_plot_structure(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 4: Story structure/plot summary."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have previous steps
        if (
            not story.get_step_content(1)
            or not story.get_step_content(2)
            or not story.get_step_content(3)
        ):
            raise HTTPException(
                status_code=400,
                detail="Steps 1-3 are required to generate plot structure",
            )

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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_character_synopses",
    response_model=StoryDetailResponse,
)
async def generate_character_synopses(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 5: Character synopses."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have previous steps
        if not all(story.get_step_content(i) for i in range(1, 5)):
            raise HTTPException(
                status_code=400,
                detail="Steps 1-4 are required to generate character synopses",
            )

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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_detailed_synopsis",
    response_model=StoryDetailResponse,
)
async def generate_detailed_synopsis(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 6: Detailed story synopsis."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have previous steps
        if not all(story.get_step_content(i) for i in range(1, 6)):
            raise HTTPException(
                status_code=400,
                detail="Steps 1-5 are required to generate detailed synopsis",
            )

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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_character_charts",
    response_model=StoryDetailResponse,
)
async def generate_character_charts(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 7: Detailed character charts."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have required previous steps (Steps 3 and 5)
        if not story.get_step_content(3) or not story.get_step_content(5):
            raise HTTPException(
                status_code=400,
                detail="Steps 3 and 5 are required to generate character charts",
            )

        # Generate character charts using workflow business logic
        workflow = SnowflakeWorkflow()
        success, character_charts, errors = workflow.handle_character_charts_generation(
            story
        )

        if not success:
            error_details = "; ".join(errors) if errors else "Unknown error"
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate character charts: {error_details}",
            )

        # Convert character charts dict to JSON string for storage
        import json

        charts_json = json.dumps(character_charts, indent=2)

        # Save the generated content to step 7
        story.set_step_content(7, charts_json)

        # If this is advancing to step 7, update current_step
        current_step = story.get_current_step()
        if current_step < 7:
            story.data["current_step"] = 7

        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_scene_breakdown",
    response_model=StoryDetailResponse,
)
async def generate_scene_breakdown(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 8: Scene breakdown/list."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have required previous step (Step 6 - detailed synopsis)
        if not story.get_step_content(6):
            raise HTTPException(
                status_code=400,
                detail="Step 6 is required to generate scene breakdown",
            )

        # Generate scene breakdown using workflow
        workflow = SnowflakeWorkflow()
        scene_breakdown = workflow.generate_scene_breakdown(story)

        # Save the generated content to step 8
        story.set_step_content(8, scene_breakdown)

        # If this is advancing to step 8, update current_step
        current_step = story.get_current_step()
        if current_step < 8:
            story.data["current_step"] = 8

        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post(
    "/api/stories/{story_id}/generate_scene_expansions",
    response_model=StoryDetailResponse,
)
async def generate_scene_expansions(
    story_id: str, session: AsyncSession = Depends(get_db)
):
    """Generate Step 9: Scene expansions (detailed scene outlines)."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have required previous step (Step 8 - scene breakdown)
        if not story.get_step_content(8):
            raise HTTPException(
                status_code=400,
                detail="Step 8 is required to generate scene expansions",
            )

        # Generate scene expansions using workflow
        workflow = SnowflakeWorkflow()
        success, scene_expansions, errors = workflow.handle_scene_expansions_generation(
            story
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate scene expansions: {'; '.join(errors)}",
            )

        # Convert scene expansions dict to JSON string for storage
        import json

        scene_expansions_json = json.dumps(scene_expansions, ensure_ascii=False)

        # Save the generated content to step 9
        story.set_step_content(9, scene_expansions_json)

        # If this is advancing to step 9, update current_step
        current_step = story.get_current_step()
        if current_step < 9:
            story.data["current_step"] = 9

        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


class SceneImprovementRequest(BaseModel):
    scene_number: int
    improvement_instructions: str


@app.post(
    "/api/stories/{story_id}/improve_scene",
    response_model=StoryDetailResponse,
)
async def improve_scene(
    story_id: str,
    request: SceneImprovementRequest,
    session: AsyncSession = Depends(get_db),
):
    """Improve a specific scene with targeted feedback."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Ensure we have Step 9 content (scene expansions)
        if not story.get_step_content(9):
            raise HTTPException(
                status_code=400,
                detail="Step 9 scene expansions are required to improve individual scenes",
            )

        # Improve the specific scene using workflow
        workflow = SnowflakeWorkflow()
        improved_content = workflow.improve_scene(
            story, request.scene_number, request.improvement_instructions
        )

        # Save the improved content back to step 9
        story.set_step_content(9, improved_content)
        await storage.save_story(story)

        return StoryDetailResponse(
            story_id=story.story_id,
            slug=story.slug,
            story_idea=story.data.get("story_idea", ""),
            current_step=story.get_current_step(),
            created_at=story.data.get("created_at"),
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.get("/api/stories/{story_id}/export_pdf")
async def export_story_pdf(story_id: str, session: AsyncSession = Depends(get_db)):
    """Export story as PDF document."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        # Generate PDF
        pdf_bytes = generate_story_pdf(story)

        # Create filename
        safe_slug = story.slug.replace(" ", "_").replace("/", "_")
        filename = f"snowflake_method_{safe_slug}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post("/api/stories/{story_id}/generate_chapter/stream")
async def generate_chapter_stream(
    story_id: str, request: Dict[str, Any], session: AsyncSession = Depends(get_db)
):
    """Generate a full chapter with streaming response."""

    async def generate():
        try:
            storage = AsyncSQLiteStorage(session)
            story = await storage.load_story(story_id)

            chapter_number = request.get("chapter_number", 1)
            writing_style = request.get("writing_style", "")

            # Get scene expansions from step 9
            scene_expansions_json = story.get_step_content(9)
            if not scene_expansions_json:
                yield f"data: {json.dumps({'error': 'Step 9 scene expansions are required to generate chapters'})}\n\n"
                return

            # Parse scene expansions
            try:
                scene_expansions = json.loads(scene_expansions_json)
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'error': 'Invalid scene expansions format'})}\n\n"
                return

            # Find the scene for this chapter
            scene_data = None
            if isinstance(scene_expansions, dict):
                # Try to find by scene number
                for key, scene in scene_expansions.items():
                    if scene.get("scene_number") == chapter_number:
                        scene_data = scene
                        break
                # If not found by scene_number, try by key
                if not scene_data:
                    scene_data = scene_expansions.get(str(chapter_number))
            elif isinstance(scene_expansions, list) and chapter_number <= len(
                scene_expansions
            ):
                scene_data = scene_expansions[chapter_number - 1]

            if not scene_data:
                yield f"data: {json.dumps({'error': f'Chapter {chapter_number} not found in scene expansions'})}\n\n"
                return

            # Send initial metadata
            yield f"data: {json.dumps({'type': 'metadata', 'chapter_number': chapter_number, 'title': scene_data.get('title', f'Chapter {chapter_number}')})}\n\n"

            # Generate the chapter using workflow
            workflow = SnowflakeWorkflow()

            # Clear any chapters after this one if regenerating
            chapters_data = story.data.get("chapters", {})
            if str(chapter_number) in chapters_data:
                # This is a regeneration - clear all chapters after this one
                chapters_to_remove = [
                    str(i) for i in range(chapter_number + 1, 20)
                ]  # Assuming max 20 chapters
                for ch_num in chapters_to_remove:
                    if ch_num in chapters_data:
                        del chapters_data[ch_num]
                story.data["chapters"] = chapters_data

            # Get previous chapters for context (if any)
            previous_chapters = []
            previous_chapter_content = None

            for i in range(1, chapter_number):
                if str(i) in chapters_data:
                    ch_data = chapters_data[str(i)]
                    previous_chapters.append(
                        {"chapter_number": i, "summary": ch_data.get("summary", "")}
                    )
                    # Get the most recent chapter's full content for style matching
                    if i == chapter_number - 1:
                        previous_chapter_content = ch_data.get("content", "")

            # Generate the chapter prose with streaming
            full_content = ""
            async for chunk in workflow.agent.generate_chapter_prose_stream(
                story_context=workflow._get_story_context(story),
                scene_data=scene_data,
                chapter_number=chapter_number,
                previous_chapters=previous_chapters,
                writing_style=writing_style,
                previous_chapter_content=previous_chapter_content,
            ):
                full_content += chunk
                # Send each chunk as SSE
                yield f"data: {json.dumps({'type': 'content', 'content': chunk})}\n\n"

            # Count words
            word_count = len(full_content.split())

            # Store the generated chapter
            if "chapters" not in story.data:
                story.data["chapters"] = {}

            story.data["chapters"][str(chapter_number)] = {
                "content": full_content,
                "word_count": word_count,
                "generated_at": datetime.now().isoformat(),
                "scene_title": scene_data.get("title", f"Chapter {chapter_number}"),
                "summary": f"Chapter {chapter_number}: {scene_data.get('title', '')} - {scene_data.get('scene_goal', '')[:100]}...",
            }

            await storage.save_story(story)

            # Send completion signal
            yield f"data: {json.dumps({'type': 'complete', 'word_count': word_count})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/stories/{story_id}/generate_chapter")
async def generate_chapter(
    story_id: str, request: Dict[str, Any], session: AsyncSession = Depends(get_db)
):
    """Generate a full chapter based on scene expansion."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        chapter_number = request.get("chapter_number", 1)
        writing_style = request.get("writing_style", "")

        # Get scene expansions from step 9
        scene_expansions_json = story.get_step_content(9)
        if not scene_expansions_json:
            raise HTTPException(
                status_code=400,
                detail="Step 9 scene expansions are required to generate chapters",
            )

        # Parse scene expansions
        try:
            scene_expansions = json.loads(scene_expansions_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid scene expansions format"
            )

        # Find the scene for this chapter
        scene_data = None
        if isinstance(scene_expansions, dict):
            # Try to find by scene number
            for key, scene in scene_expansions.items():
                if scene.get("scene_number") == chapter_number:
                    scene_data = scene
                    break
            # If not found by scene_number, try by key
            if not scene_data:
                scene_data = scene_expansions.get(str(chapter_number))
        elif isinstance(scene_expansions, list) and chapter_number <= len(
            scene_expansions
        ):
            scene_data = scene_expansions[chapter_number - 1]

        if not scene_data:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter_number} not found in scene expansions",
            )

        # Generate the chapter using workflow
        workflow = SnowflakeWorkflow()

        # Clear any chapters after this one if regenerating
        chapters_data = story.data.get("chapters", {})
        if str(chapter_number) in chapters_data:
            # This is a regeneration - clear all chapters after this one
            chapters_to_remove = [
                str(i) for i in range(chapter_number + 1, 20)
            ]  # Assuming max 20 chapters
            for ch_num in chapters_to_remove:
                if ch_num in chapters_data:
                    del chapters_data[ch_num]
            story.data["chapters"] = chapters_data

        # Get previous chapters for context (if any)
        previous_chapters = []
        previous_chapter_content = None

        for i in range(1, chapter_number):
            if str(i) in chapters_data:
                ch_data = chapters_data[str(i)]
                previous_chapters.append(
                    {"chapter_number": i, "summary": ch_data.get("summary", "")}
                )
                # Get the most recent chapter's full content for style matching
                if i == chapter_number - 1:
                    previous_chapter_content = ch_data.get("content", "")

        # Generate the chapter prose
        chapter_content = workflow.generate_chapter_prose(
            story=story,
            scene_data=scene_data,
            chapter_number=chapter_number,
            previous_chapters=previous_chapters,
            writing_style=writing_style,
            previous_chapter_content=previous_chapter_content,
        )

        # Count words
        word_count = len(chapter_content.split())

        # Store the generated chapter
        if "chapters" not in story.data:
            story.data["chapters"] = {}

        story.data["chapters"][str(chapter_number)] = {
            "content": chapter_content,
            "word_count": word_count,
            "generated_at": datetime.now().isoformat(),
            "scene_title": scene_data.get("title", f"Chapter {chapter_number}"),
            "summary": f"Chapter {chapter_number}: {scene_data.get('title', '')} - {scene_data.get('scene_goal', '')[:100]}...",
        }

        await storage.save_story(story)

        return {
            "content": chapter_content,
            "word_count": word_count,
            "chapter_number": chapter_number,
            "title": scene_data.get("title", f"Chapter {chapter_number}"),
        }

    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post("/api/stories/{story_id}/refine_chapter")
async def refine_chapter(
    story_id: str, request: Dict[str, Any], session: AsyncSession = Depends(get_db)
):
    """Refine an existing chapter with specific instructions."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        chapter_number = request.get("chapter_number")
        instructions = request.get("instructions", "")

        if not chapter_number:
            raise HTTPException(status_code=400, detail="Chapter number is required")
        if not instructions.strip():
            raise HTTPException(
                status_code=400, detail="Refinement instructions are required"
            )

        # Get existing chapters data
        chapters_data = story.data.get("chapters", {})
        if str(chapter_number) not in chapters_data:
            raise HTTPException(
                status_code=404, detail=f"Chapter {chapter_number} not found"
            )

        # Check if this is the most recent chapter (only most recent can be refined)
        completed_chapters = [
            int(num)
            for num in chapters_data.keys()
            if chapters_data[num].get("content")
        ]
        if not completed_chapters:
            raise HTTPException(status_code=400, detail="No completed chapters found")

        most_recent_chapter = max(completed_chapters)
        if chapter_number != most_recent_chapter:
            raise HTTPException(
                status_code=400,
                detail=f"Only the most recent chapter (Chapter {most_recent_chapter}) can be refined",
            )

        current_chapter = chapters_data[str(chapter_number)]
        current_content = current_chapter.get("content", "")

        if not current_content:
            raise HTTPException(
                status_code=400,
                detail=f"Chapter {chapter_number} has no content to refine",
            )

        # Get scene data for context
        scene_expansions_json = story.get_step_content(9)
        if not scene_expansions_json:
            raise HTTPException(
                status_code=400,
                detail="Step 9 scene expansions are required for chapter refinement",
            )

        try:
            scene_expansions = json.loads(scene_expansions_json)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid scene expansions format"
            )

        # Find the scene data for this chapter
        scene_data = None
        if isinstance(scene_expansions, dict):
            for key, scene in scene_expansions.items():
                if scene.get("scene_number") == chapter_number:
                    scene_data = scene
                    break
            if not scene_data:
                scene_data = scene_expansions.get(str(chapter_number))
        elif isinstance(scene_expansions, list) and chapter_number <= len(
            scene_expansions
        ):
            scene_data = scene_expansions[chapter_number - 1]

        if not scene_data:
            raise HTTPException(
                status_code=404,
                detail=f"Scene data for Chapter {chapter_number} not found",
            )

        # Refine the chapter using workflow
        workflow = SnowflakeWorkflow()
        refined_content = workflow.refine_chapter_prose(
            story=story,
            chapter_number=chapter_number,
            current_content=current_content,
            scene_data=scene_data,
            instructions=instructions,
        )

        # Count words
        word_count = len(refined_content.split())

        # Update the stored chapter
        story.data["chapters"][str(chapter_number)] = {
            **current_chapter,
            "content": refined_content,
            "word_count": word_count,
            "generated_at": datetime.now().isoformat(),
            "refined": True,
            "refinement_instructions": instructions,
        }

        await storage.save_story(story)

        return {
            "content": refined_content,
            "word_count": word_count,
            "chapter_number": chapter_number,
            "title": current_chapter.get("scene_title", f"Chapter {chapter_number}"),
        }

    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.get("/api/stories/{story_id}/export_novel")
async def export_novel(story_id: str, session: AsyncSession = Depends(get_db)):
    """Export the generated novel as a text file."""
    try:
        storage = AsyncSQLiteStorage(session)
        story = await storage.load_story(story_id)

        chapters_data = story.data.get("chapters", {})
        if not chapters_data:
            raise HTTPException(
                status_code=400, detail="No chapters have been generated yet"
            )

        # Compile all chapters into a single document
        novel_content = f"{story.slug.upper()}\n\n"
        novel_content += "Created with the Snowflake Method\n"
        novel_content += f"{'=' * 50}\n\n"

        # Add each chapter in order
        chapter_numbers = sorted([int(num) for num in chapters_data.keys()])
        for chapter_num in chapter_numbers:
            chapter_data = chapters_data[str(chapter_num)]
            title = chapter_data.get("scene_title", f"Chapter {chapter_num}")
            content = chapter_data.get("content", "")

            novel_content += f"\n\nCHAPTER {chapter_num}: {title}\n"
            novel_content += f"{'-' * 50}\n\n"
            novel_content += content
            novel_content += "\n\n"

        # Add metadata at the end
        total_words = sum(ch.get("word_count", 0) for ch in chapters_data.values())
        novel_content += f"\n\n{'=' * 50}\n"
        novel_content += f"Total word count: {total_words:,}\n"
        novel_content += f"Chapters: {len(chapters_data)}\n"
        novel_content += f"Generated on: {datetime.now().strftime('%B %d, %Y')}\n"

        # Create filename
        safe_slug = story.slug.replace(" ", "_").replace("/", "_")
        filename = f"{safe_slug}_novel.txt"

        return Response(
            content=novel_content.encode("utf-8"),
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.post("/api/stories/{story_id}/next", response_model=StoryDetailResponse)
async def advance_story(story_id: str, session: AsyncSession = Depends(get_db)):
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
            steps={str(k): v for k, v in story.data.get("steps", {}).items()},
        )
    except StoryNotFoundError:
        raise HTTPException(status_code=404, detail="Story not found")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Snowflake Method API",
        "description": "AI-powered writing assistant based on Randy Ingermanson's Snowflake Method",
        "method_info": "https://www.advancedfictionwriting.com/articles/snowflake-method/",
        "built_by": "Joel Grus (@joelgrus)",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker and monitoring."""
    return {"status": "healthy", "service": "snowmeth-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
