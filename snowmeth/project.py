"""Refactored project and story management for dual CLI/Web support."""

from typing import Optional, List

from .storage import StorageBackend, FileStorage, Story
from .context import OperationContext, CLIContext
from .exceptions import StoryNotFoundError


class ProjectManager:
    """Manages multiple snowflake stories with pluggable storage and context."""
    
    def __init__(self, 
                 storage: Optional[StorageBackend] = None, 
                 context: Optional[OperationContext] = None):
        self.storage = storage or FileStorage()
        self.context = context or CLIContext()
        
        # Set up save callback for stories
        self._setup_story_save_callback()
    
    def _setup_story_save_callback(self) -> None:
        """Set up the save callback for Story instances."""
        # Monkey patch the Story.save method to use our storage
        def story_save(story_instance):
            self.storage.save_story(story_instance)
        
        # This will affect all Story instances created through this manager
        Story.save = story_save
    
    def create_story(self, slug: str, story_idea: str) -> Story:
        """Create a new story."""
        story = self.storage.create_story(slug, story_idea)
        
        # Set as current story in CLI mode
        if isinstance(self.context, CLIContext):
            self.context.set_current_story_identifier(story.slug)
        
        return story
    
    def get_story(self, identifier: str) -> Story:
        """Get a story by slug or UUID."""
        return self.storage.load_story(identifier)
    
    def get_current_story(self) -> Optional[Story]:
        """Get the current active story (CLI mode) or context story (Web mode)."""
        identifier = self.context.get_current_story_identifier()
        if not identifier:
            return None
        
        try:
            return self.storage.load_story(identifier)
        except StoryNotFoundError:
            # Clear invalid reference
            self.context.clear_current_story()
            return None
    
    def switch_story(self, identifier: str) -> None:
        """Switch to a different story (CLI mode only)."""
        # Verify story exists
        story = self.storage.load_story(identifier)  # Will raise if not found
        
        # Update context
        self.context.set_current_story_identifier(story.slug)
    
    def list_stories(self) -> List[Story]:
        """List all stories."""
        return self.storage.list_stories()
    
    def delete_story(self, identifier: str) -> None:
        """Delete a story."""
        # Check if we're deleting the current story
        current_identifier = self.context.get_current_story_identifier()
        story = self.storage.load_story(identifier)  # Verify it exists
        
        # Delete the story
        self.storage.delete_story(identifier)
        
        # Clear current story if we just deleted it
        if current_identifier in (story.slug, story.story_id):
            self.context.clear_current_story()
    
    @property
    def stories_dir(self):
        """Get stories directory (for CLI compatibility)."""
        if hasattr(self.storage, 'stories_dir'):
            return self.storage.stories_dir
        return None


# Legacy compatibility - maintain the old Story class interface
# This allows existing code to continue working
class LegacyStory:
    """Legacy Story class for backward compatibility."""
    
    def __init__(self, story: Story):
        self._story = story
        self.data = story.data
        self.file_path = getattr(story, 'file_path', None)
    
    def get_current_step(self) -> int:
        return self._story.get_current_step()
    
    def set_current_step(self, step: int) -> None:
        self._story.set_current_step(step)
    
    def get_step_content(self, step: int) -> Optional[str]:
        return self._story.get_step_content(step)
    
    def set_step_content(self, step: int, content: str) -> None:
        self._story.set_step_content(step, content)
    
    def can_advance_to_step(self, target_step: int) -> bool:
        return self._story.can_advance_to_step(target_step)
    
    def get_story_context(self, up_to_step: int) -> str:
        return self._story.get_story_context(up_to_step)
    
    def save(self) -> None:
        self._story.save()
    
    @property
    def story_id(self) -> str:
        return self._story.story_id
    
    @property 
    def slug(self) -> str:
        return self._story.slug