#!/usr/bin/env python3

import json
from snowmeth.project import ProjectManager

def main():
    manager = ProjectManager()
    story = manager.get_current_story()
    
    # Get Step 8 content and extract scene list
    step8_raw = story.data['steps']['8']['content']
    
    # Strip markdown formatting
    if step8_raw.startswith('```json'):
        step8_content = step8_raw[7:-3].strip()  # Remove ```json and ```
    else:
        step8_content = step8_raw
    
    scenes = json.loads(step8_content)
    print(f'Total scenes in Step 8: {len(scenes)}')
    print('Scene numbers:', [scene.get('scene_number') for scene in scenes])
    
    # Create a proper Step 9 structure with placeholders for all scenes
    step9_scenes = {}
    for scene in scenes:
        scene_num = scene.get('scene_number')
        if scene_num:
            # Create a placeholder expansion for each scene
            step9_scenes[f"scene_{scene_num}"] = {
                "scene_number": scene_num,
                "title": f"Scene {scene_num} - Placeholder",
                "pov_character": scene.get('pov_character', 'Unknown'),
                "setting": "Placeholder setting - needs expansion",
                "scene_goal": "Placeholder goal - needs expansion",
                "character_goal": "Placeholder character goal - needs expansion",
                "character_motivation": "Placeholder motivation - needs expansion",
                "obstacles": ["Placeholder obstacle - needs expansion"],
                "conflict_type": "Placeholder conflict type - needs expansion",
                "key_beats": ["Placeholder beat - needs expansion"],
                "emotional_arc": "Placeholder emotional arc - needs expansion",
                "scene_outcome": "Placeholder outcome - needs expansion",
                "subplot_elements": ["Placeholder subplot - needs expansion"],
                "character_relationships": "Placeholder relationships - needs expansion",
                "foreshadowing": "Placeholder foreshadowing - needs expansion",
                "estimated_pages": scene.get('estimated_pages', 8)
            }
    
    # Save the corrected Step 9 content
    step9_content = json.dumps(step9_scenes, indent=2)
    story.set_step_content(9, step9_content)
    story.save()
    
    print(f'\n✓ Fixed Step 9 with {len(step9_scenes)} scene placeholders')
    print('Scene keys:', list(step9_scenes.keys()))

if __name__ == "__main__":
    main()