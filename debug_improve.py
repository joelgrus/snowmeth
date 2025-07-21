#!/usr/bin/env python3

import json
import re
from snowmeth.project import ProjectManager
from snowmeth.workflow import SnowflakeWorkflow

def debug_improve_all():
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    story = manager.get_current_story()

    if not story:
        print("No current story.")
        return

    # Check if we have analysis
    analysis_file = manager.stories_dir / f"{story.data['slug']}-analysis.json"
    if not analysis_file.exists():
        print("No analysis found.")
        return
    
    try:
        print("1. Loading analysis...")
        # Load analysis
        with open(analysis_file, 'r') as f:
            analysis_data = json.loads(f.read())
        
        print("2. Extracting recommendations...")
        # Extract issues and identify problematic scenes
        recommendations = analysis_data.get("recommendations", {})
        high_priority = recommendations.get("high_priority", [])
        medium_priority = recommendations.get("medium_priority", [])
        
        if not high_priority and not medium_priority:
            print("No issues found.")
            return
        
        print("3. Getting scene list...")
        # Find scenes mentioned in issues
        scene_list = workflow.get_scene_list(story)
        print(f"Scene list type: {type(scene_list)}, length: {len(scene_list)}")
        
        print("4. Finding scenes to improve...")
        scenes_to_improve = set()
        
        # Look for scene numbers and character names in issues
        for issue in high_priority + medium_priority:
            print(f"Processing issue: {issue[:50]}...")
            # Look for "Scene N" patterns
            scene_matches = re.findall(r'Scene (\d+)', issue)
            for match in scene_matches:
                scenes_to_improve.add(int(match))
            
            # Look for character names (POV characters)
            for scene in scene_list:
                pov = scene.get("pov_character", "")
                scene_num = scene.get("scene_number")
                print(f"  Checking scene {scene_num} (POV: {pov}) - type: {type(scene_num)}")
                if pov and pov in issue:
                    if scene_num:
                        print(f"    Adding scene {scene_num} to improve list")
                        scenes_to_improve.add(scene_num)
        
        print("5. Processing scenes to improve...")
        # If no specific scenes found, improve scenes with common issues
        if not scenes_to_improve:
            # Default to first few scenes for character development issues
            scenes_to_improve = {1, 2, 3, 4, 14}  # Early scenes + Malakor scenes
        
        scenes_to_improve = sorted(list(scenes_to_improve))
        total_issues = len(high_priority) + len(medium_priority)
        
        print(f"Found {total_issues} issues to address.")
        print(f"Will improve {len(scenes_to_improve)} scenes: {', '.join(map(str, scenes_to_improve))}")
        
        print("6. Testing scene improvement...")
        # Test improving just one scene
        scene_num = scenes_to_improve[0]
        print(f"Testing improvement of scene {scene_num}...")
        
        # Get current scene expansions
        step9_content = story.get_step_content(9)
        print(f"Step 9 content type: {type(step9_content)}")
        if step9_content:
            print(f"Step 9 content length: {len(step9_content)}")
        
        current_expansions = json.loads(step9_content)
        scene_key = f"scene_{scene_num}"
        
        if scene_key not in current_expansions:
            print(f"Scene {scene_num} not found in expansions.")
            return
        
        print(f"Found scene {scene_num}, attempting to improve...")
        # Improve the scene using the expand_scene method with feedback
        improved_scene = workflow.expand_scene(story, scene_num)
        print(f"Improved scene type: {type(improved_scene)}")
        print(f"Improved scene length: {len(improved_scene)}")
        
        print("✅ Debug completed successfully!")
        
    except Exception as e:
        import traceback
        print(f"Error during improvement: {e}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_improve_all()