#!/usr/bin/env python3

from snowflake import Project

def test_project_creation():
    """Test basic project functionality without AI"""
    
    # Test project creation
    project = Project()
    
    # Manually set some data
    project.data["project_name"] = "Test Novel"
    project.data["story_idea"] = "a boy who likes to play baseball but is no good at it"
    project.set_step_content(1, "A young boy struggles to improve at baseball despite his passion for the game.")
    
    # Save and reload
    project.save()
    
    # Create new project instance to test loading
    project2 = Project()
    
    print(f"Project name: {project2.data['project_name']}")
    print(f"Story idea: {project2.data['story_idea']}")
    print(f"Step 1 content: {project2.get_step_content(1)}")
    
    print("✓ Basic project functionality works!")

if __name__ == "__main__":
    test_project_creation()