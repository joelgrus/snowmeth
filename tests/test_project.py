"""Tests for project/story management."""

from snowmeth.storage import Story


class TestStory:
    """Test Story class functionality."""

    def test_story_creation(self):
        """Test basic story creation."""
        story_data = {
            "slug": "test-story",
            "story_idea": "A test story about testing",
            "current_step": 1,
            "steps": {"1": "This is a test sentence."},
        }
        story_data["story_id"] = "test-id"
        story = Story(story_data)

        assert story.story_id == "test-id"
        assert story.data["slug"] == "test-story"
        assert story.get_current_step() == 1

    def test_get_step_content(self):
        """Test getting step content."""
        story_data = {
            "slug": "test-story",
            "story_idea": "A test story",
            "current_step": 2,
            "steps": {"1": "First step content.", "2": "Second step content."},
        }
        story_data["story_id"] = "test-id"
        story = Story(story_data)

        assert story.get_step_content(1) == "First step content."
        assert story.get_step_content(2) == "Second step content."
        assert story.get_step_content(3) is None

    def test_can_advance_to_step(self):
        """Test step advancement validation."""
        story_data = {
            "slug": "test-story",
            "story_idea": "A test story",
            "current_step": 1,
            "steps": {"1": "First step content."},
        }
        story_data["story_id"] = "test-id"
        story = Story(story_data)

        # Should be able to advance to step 2 when step 1 has content
        assert story.can_advance_to_step(2) is True
        # Should not be able to advance to step 3 without step 2 content
        assert story.can_advance_to_step(3) is False
