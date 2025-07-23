"""SQLite storage backend for the API."""

from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..storage import Story
from ..exceptions import StoryNotFoundError, StoryAlreadyExistsError
from .database import DbStory


class AsyncSQLiteStorage:
    """Async SQLite storage backend for web API."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_story(
        self, slug: str, story_idea: str, story_id: Optional[str] = None
    ) -> Story:
        """Create a new story."""
        # Check if slug already exists
        result = await self.session.execute(
            select(DbStory).where(DbStory.slug == slug)
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise StoryAlreadyExistsError(f"Story '{slug}' already exists")

        # Create new story
        db_story = DbStory(
            story_id=story_id, slug=slug, story_idea=story_idea, steps={}, chapters={}
        )

        self.session.add(db_story)
        await self.session.commit()

        return Story(db_story.to_dict())

    async def load_story(self, identifier: str) -> Story:
        """Load a story by slug or UUID."""
        # Try by UUID first
        db_story = await self.session.get(DbStory, identifier)

        if not db_story:
            # Try by slug
            result = await self.session.execute(
                select(DbStory).where(DbStory.slug == identifier)
            )
            db_story = result.scalar_one_or_none()

        if not db_story:
            raise StoryNotFoundError(f"Story '{identifier}' not found")

        return Story(db_story.to_dict())

    async def save_story(self, story: Story) -> None:
        """Save a story."""
        db_story = await self.session.get(DbStory, story.story_id)

        if not db_story:
            # Create new if doesn't exist
            db_story = DbStory(
                story_id=story.story_id,
                slug=story.slug,
                story_idea=story.data.get("story_idea", ""),
                current_step=story.data.get("current_step", 1),
                steps=story.data.get("steps", {}),
                chapters=story.data.get("chapters", {}),
                writing_style=story.data.get("writing_style"),
            )
            self.session.add(db_story)
        else:
            # Update existing
            db_story.slug = story.slug
            db_story.story_idea = story.data.get("story_idea", "")
            db_story.current_step = story.data.get("current_step", 1)
            db_story.steps = story.data.get("steps", {})
            db_story.chapters = story.data.get("chapters", {})
            db_story.writing_style = story.data.get("writing_style")

        await self.session.commit()

    async def list_stories(self) -> List[Story]:
        """List all stories."""
        result = await self.session.execute(
            select(DbStory).order_by(DbStory.created_at.desc())
        )
        db_stories = result.scalars().all()

        return [Story(db_story.to_dict()) for db_story in db_stories]

    async def delete_story(self, identifier: str) -> None:
        """Delete a story by slug or UUID."""
        # Load to verify it exists
        story = await self.load_story(identifier)

        # Delete by UUID
        await self.session.execute(
            delete(DbStory).where(DbStory.story_id == story.story_id)
        )
        await self.session.commit()

    async def update_writing_style(self, story_id: str, writing_style: str) -> None:
        """Update the writing style for a story."""
        db_story = await self.session.get(DbStory, story_id)
        if not db_story:
            raise StoryNotFoundError(f"Story '{story_id}' not found")

        db_story.writing_style = writing_style
        await self.session.commit()

    async def story_exists(self, identifier: str) -> bool:
        """Check if a story exists by slug or UUID."""
        try:
            await self.load_story(identifier)
            return True
        except StoryNotFoundError:
            return False
