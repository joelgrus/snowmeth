"""Storage abstraction layer for Snowflake Method stories."""

import json
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any

from .exceptions import StoryNotFoundError, StoryAlreadyExistsError


class StorageBackend(ABC):
    """Abstract base class for story storage backends."""

    @abstractmethod
    def create_story(
        self, slug: str, story_idea: str, story_id: Optional[str] = None
    ) -> "Story":
        """Create a new story."""
        pass

    @abstractmethod
    def load_story(self, identifier: str) -> "Story":
        """Load a story by slug or UUID."""
        pass

    @abstractmethod
    def save_story(self, story: "Story") -> None:
        """Save a story."""
        pass

    @abstractmethod
    def list_stories(self) -> List["Story"]:
        """List all stories."""
        pass

    @abstractmethod
    def delete_story(self, identifier: str) -> None:
        """Delete a story by slug or UUID."""
        pass

    @abstractmethod
    def story_exists(self, identifier: str) -> bool:
        """Check if a story exists by slug or UUID."""
        pass


class FileStorage(StorageBackend):
    """File-based storage backend for CLI compatibility."""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.snowmeth_dir = self.project_dir / ".snowmeth"
        self.stories_dir = self.snowmeth_dir / "stories"

        # Ensure directories exist
        self.stories_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_slug(self, slug: str) -> str:
        """Convert slug to safe filename."""
        import re

        # Replace spaces and special chars with hyphens, lowercase
        sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "-", slug.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r"-+", "-", sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip("-")

    def _get_story_file_path(self, slug: str) -> Path:
        """Get file path for a story slug."""
        clean_slug = self._sanitize_slug(slug)
        return self.stories_dir / f"{clean_slug}.json"

    def _load_story_from_file(self, file_path: Path) -> "Story":
        """Load story from a file path."""
        with open(file_path, "r") as f:
            story_data = json.load(f)

        # Ensure story has UUID
        if "story_id" not in story_data:
            story_data["story_id"] = str(uuid.uuid4())
            # Save back with UUID
            with open(file_path, "w") as f:
                json.dump(story_data, f, indent=2)

        return Story(story_data, file_path)

    def _find_story_by_uuid(self, story_id: str) -> Optional[Path]:
        """Find story file by UUID."""
        for story_file in self.stories_dir.glob("*.json"):
            try:
                with open(story_file, "r") as f:
                    data = json.load(f)
                if data.get("story_id") == story_id:
                    return story_file
            except (json.JSONDecodeError, IOError):
                continue
        return None

    def create_story(
        self, slug: str, story_idea: str, story_id: Optional[str] = None
    ) -> "Story":
        """Create a new story."""
        clean_slug = self._sanitize_slug(slug)
        story_file = self._get_story_file_path(slug)

        if story_file.exists():
            raise StoryAlreadyExistsError(f"Story '{clean_slug}' already exists")

        story_data = {
            "story_id": story_id or str(uuid.uuid4()),
            "slug": clean_slug,
            "story_idea": story_idea,
            "current_step": 1,
            "steps": {},
            "created_at": self._get_timestamp(),
        }

        story = Story(story_data, story_file)
        self.save_story(story)
        return story

    def load_story(self, identifier: str) -> "Story":
        """Load a story by slug or UUID."""
        # Try loading by slug first
        story_file = self._get_story_file_path(identifier)
        if story_file.exists():
            return self._load_story_from_file(story_file)

        # Try loading by UUID
        story_file = self._find_story_by_uuid(identifier)
        if story_file:
            return self._load_story_from_file(story_file)

        raise StoryNotFoundError(f"Story '{identifier}' not found")

    def save_story(self, story: "Story") -> None:
        """Save a story."""
        if not story.file_path:
            # Create new file path based on slug
            story.file_path = self._get_story_file_path(story.data["slug"])

        with open(story.file_path, "w") as f:
            json.dump(story.data, f, indent=2)

    def list_stories(self) -> List["Story"]:
        """List all stories."""
        stories = []
        for story_file in self.stories_dir.glob("*.json"):
            try:
                story = self._load_story_from_file(story_file)
                stories.append(story)
            except (json.JSONDecodeError, IOError):
                continue

        # Sort by creation time
        return sorted(stories, key=lambda s: s.data.get("created_at", ""))

    def delete_story(self, identifier: str) -> None:
        """Delete a story by slug or UUID."""
        story = self.load_story(identifier)  # This will raise if not found
        if story.file_path and story.file_path.exists():
            story.file_path.unlink()

    def story_exists(self, identifier: str) -> bool:
        """Check if a story exists by slug or UUID."""
        try:
            self.load_story(identifier)
            return True
        except StoryNotFoundError:
            return False

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()


class Story:
    """Represents a Snowflake Method story with UUID support."""

    def __init__(self, data: Dict[str, Any], file_path: Optional[Path] = None):
        self.data = data
        self.file_path = file_path

        # Ensure story has UUID
        if "story_id" not in self.data:
            self.data["story_id"] = str(uuid.uuid4())

    @property
    def story_id(self) -> str:
        """Get the story UUID."""
        return self.data["story_id"]

    @property
    def slug(self) -> str:
        """Get the story slug."""
        return self.data.get("slug", "")

    def get_current_step(self) -> int:
        """Get the current step number."""
        # If current_step is explicitly set, use it
        if "current_step" in self.data:
            return self.data["current_step"]

        # Otherwise, calculate from highest step with content
        steps = self.data.get("steps", {})
        if not steps:
            return 1

        # Find the highest step number that has content
        max_step = 1
        for step_str in steps.keys():
            try:
                step_num = int(step_str)
                if self.get_step_content(step_num) is not None:
                    max_step = max(max_step, step_num)
            except ValueError:
                continue

        return max_step

    def set_current_step(self, step: int) -> None:
        """Set the current step number."""
        self.data["current_step"] = step

    def get_step_content(self, step: int) -> Optional[str]:
        """Get content for a specific step."""
        step_data = self.data.get("steps", {}).get(str(step))
        if step_data is None:
            return None

        # Handle legacy format where steps were objects with 'content' field
        if isinstance(step_data, dict) and "content" in step_data:
            return step_data["content"]

        # Handle new format where steps are just strings
        if isinstance(step_data, str):
            return step_data

        return None

    def set_step_content(self, step: int, content: str) -> None:
        """Set content for a specific step."""
        if "steps" not in self.data:
            self.data["steps"] = {}
        self.data["steps"][str(step)] = content

        # Update current step if this is the next step
        if step > self.get_current_step():
            self.set_current_step(step)

    def can_advance_to_step(self, target_step: int) -> bool:
        """Check if we can advance to a target step."""
        if target_step <= 1:
            return True

        # Check if previous step has content
        previous_step = target_step - 1
        return self.get_step_content(previous_step) is not None

    def get_story_context(self, up_to_step: int) -> str:
        """Get story context up to a specific step."""
        context_parts = [f"Story Idea: {self.data.get('story_idea', '')}"]

        for step in range(1, up_to_step + 1):
            content = self.get_step_content(step)
            if content:
                context_parts.append(f"Step {step}: {content}")

        return "\n\n".join(context_parts)

    def save(self) -> None:
        """Save the story (requires storage backend)."""
        # This will be called by the storage backend
        # For now, this is a placeholder that gets overridden by ProjectManager
        pass
