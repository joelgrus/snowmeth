#!/usr/bin/env python3

from snowmeth.project import ProjectManager


def test_project_creation():
    """Test basic project functionality without AI"""

    # Test project creation
    manager = ProjectManager()
    
    # Create a test story
    story = manager.create_story("test-story", "a boy who likes to play baseball but is no good at it")
    
    # Manually set some data
    story.set_step_content(
        1,
        "A young boy struggles to improve at baseball despite his passion for the game.",
    )
    story.save()

    # Test retrieval
    retrieved_story = manager.get_current_story()
    
    assert retrieved_story is not None
    assert retrieved_story.data['slug'] == "test-story"
    assert retrieved_story.data['story_idea'] == "a boy who likes to play baseball but is no good at it"
    assert retrieved_story.get_step_content(1) == "A young boy struggles to improve at baseball despite his passion for the game."

    print(f"Story slug: {retrieved_story.data['slug']}")
    print(f"Story idea: {retrieved_story.data['story_idea']}")
    print(f"Step 1 content: {retrieved_story.get_step_content(1)}")

    print("✓ Basic project functionality works!")


if __name__ == "__main__":
    test_project_creation()
