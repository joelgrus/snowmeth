"""Snowflake Method workflow and progression logic."""

from typing import Optional, Tuple, List, Dict, Any
import json

from .agents import SnowflakeAgent
from .project import Story


class SnowflakeWorkflow:
    """Handles step progression and AI interactions for the Snowflake Method"""

    def __init__(self):
        self.agent = SnowflakeAgent()

    def can_advance(self, story: Story, to_step: int) -> bool:
        """Check if story can advance to the given step"""
        return story.can_advance_to_step(to_step)

    def generate_initial_sentence(self, story_idea: str) -> str:
        """Generate initial one-sentence summary for Step 1"""
        return self.agent.generate_sentence(story_idea)

    def expand_to_paragraph(self, story: Story) -> str:
        """Expand Step 1 sentence to Step 2 paragraph"""
        sentence = story.get_step_content(1)
        if not sentence:
            raise ValueError("No sentence found in step 1")

        return self.agent.expand_to_paragraph(sentence, story.data["story_idea"])

    def extract_characters(self, story: Story) -> str:
        """Extract characters for Step 3"""
        story_context = story.get_story_context(up_to_step=2)
        return self.agent.extract_characters(story_context)

    def expand_to_plot(self, story: Story) -> str:
        """Expand to detailed plot summary for Step 4"""
        story_context = story.get_story_context(up_to_step=3)
        return self.agent.expand_to_plot(story_context)

    def generate_character_synopses(self, story: Story) -> str:
        """Generate character synopses from each character's POV for Step 5"""
        story_context = story.get_story_context(up_to_step=4)
        return self.agent.generate_character_synopses(story_context)

    def expand_to_detailed_plot(self, story: Story) -> str:
        """Expand to detailed four-page plot synopsis for Step 6"""
        story_context = story.get_story_context(up_to_step=5)
        return self.agent.expand_to_detailed_plot(story_context)

    def get_character_names(self, story: Story) -> List[str]:
        """Extract character names from Step 3 character summaries"""
        characters_content = story.get_step_content(3)
        if not characters_content:
            raise ValueError("No character summaries found in Step 3")

        # Clean up potential markdown formatting
        content = characters_content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        try:
            char_dict = json.loads(content)
            return list(char_dict.keys())
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in Step 3 character summaries: {e}")

    def generate_detailed_character_chart(
        self, story: Story, character_name: str
    ) -> str:
        """Generate detailed character chart for a single character for Step 7"""
        story_context = story.get_story_context(up_to_step=6)
        return self.agent.generate_detailed_character_chart(
            story_context, character_name
        )

    def generate_scene_breakdown(self, story: Story) -> str:
        """Generate scene breakdown from four-page plot synopsis for Step 8"""
        story_context = story.get_story_context(up_to_step=7)
        return self.agent.generate_scene_breakdown(story_context)

    def get_scene_list(self, story: Story) -> List[dict]:
        """Extract scene list from Step 8 scene breakdown"""
        scene_content = story.get_step_content(8)
        if not scene_content:
            raise ValueError("No scene breakdown found in Step 8")

        # Clean up potential markdown formatting
        content = scene_content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        try:
            scene_list = json.loads(content)
            return scene_list
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in Step 8 scene breakdown: {e}")

    def expand_scene(self, story: Story, scene_number: int) -> str:
        """Expand a single scene into detailed mini-outline for Step 9"""
        scene_list = self.get_scene_list(story)
        
        # Find the specific scene
        target_scene = None
        for scene in scene_list:
            if scene.get("scene_number") == scene_number:
                target_scene = scene
                break
        
        if not target_scene:
            raise ValueError(f"Scene {scene_number} not found in scene breakdown")
        
        story_context = story.get_story_context(up_to_step=8)
        scene_info = json.dumps(target_scene)
        
        return self.agent.expand_scene(story_context, scene_info)

    def improve_scene(self, story: Story, scene_number: int, improvement_guidance: str) -> str:
        """Improve a specific scene with targeted feedback"""
        scene_list = self.get_scene_list(story)
        
        # Find the specific scene
        target_scene = None
        for scene in scene_list:
            if scene.get("scene_number") == scene_number:
                target_scene = scene
                break
        
        if not target_scene:
            raise ValueError(f"Scene {scene_number} not found in scene breakdown")
        
        # Get current scene expansion
        step9_content = story.get_step_content(9)
        if step9_content:
            current_expansions = json.loads(step9_content)
            scene_key = f"scene_{scene_number}"
            current_scene = current_expansions.get(scene_key, {})
        else:
            current_scene = {}
        
        story_context = story.get_story_context(up_to_step=8)
        scene_info = json.dumps(target_scene)
        current_expansion = json.dumps(current_scene)
        
        # Pass current expansion for fallback
        try:
            return self.agent.improve_scene(story_context, scene_info, current_expansion, improvement_guidance)
        except ValueError as e:
            # If improvement fails, return current expansion unchanged
            print(f"Scene improvement failed: {e}")
            return current_expansion


    def refine_content(self, story: Story, instructions: str) -> str:
        """Refine current step content with specific instructions"""
        current_step = story.get_current_step()
        current_content = story.get_step_content(current_step)

        if not current_content:
            raise ValueError(f"No content found for step {current_step}")

        # Map step numbers to content types
        step_types = {
            1: "sentence",
            2: "paragraph",
            3: "character",
            4: "plot",
            5: "character_synopsis",
            6: "detailed_plot",
            7: "character_chart",
            8: "scene_breakdown",
            9: "scene_expansion",
            10: "story_completion",
        }

        content_type = step_types.get(current_step, f"step-{current_step}")
        story_context = story.get_story_context(up_to_step=current_step)

        return self.agent.refine_content(
            current_content, content_type, story_context, instructions
        )

    def handle_character_charts_generation(self, story: Story) -> Tuple[bool, Dict[str, str], List[str]]:
        """
        Handle Step 7 character chart generation.
        
        Returns:
            (success, character_charts_dict, error_messages)
        """
        try:
            character_names = self.get_character_names(story)
            character_charts = {}
            errors = []
            
            for character_name in character_names:
                try:
                    chart = self.generate_detailed_character_chart(story, character_name)
                    character_charts[character_name] = chart
                except Exception as e:
                    error_msg = f"Error generating chart for {character_name}: {e}"
                    errors.append(error_msg)
                    continue
            
            success = len(character_charts) > 0
            return success, character_charts, errors
            
        except Exception as e:
            return False, {}, [f"Error in character chart generation: {e}"]

    def handle_scene_expansions_generation(self, story: Story) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Handle Step 9 scene expansion generation.
        
        Returns:
            (success, scene_expansions_dict, error_messages)
        """
        try:
            scene_list = self.get_scene_list(story)
            scene_expansions = {}
            errors = []
            
            for scene in scene_list:
                scene_num = scene.get("scene_number")
                if not scene_num:
                    errors.append("Scene missing scene_number")
                    continue
                    
                try:
                    expansion = self.expand_scene(story, scene_num)
                    # Try to parse as JSON, fallback to string
                    try:
                        scene_expansions[f"scene_{scene_num}"] = json.loads(expansion)
                    except json.JSONDecodeError:
                        scene_expansions[f"scene_{scene_num}"] = expansion
                except Exception as e:
                    error_msg = f"Error expanding Scene {scene_num}: {e}"
                    errors.append(error_msg)
                    continue
            
            success = len(scene_expansions) > 0
            return success, scene_expansions, errors
            
        except Exception as e:
            return False, {}, [f"Error in scene expansion generation: {e}"]


class AnalysisWorkflow:
    """Handles the analysis and iterative improvement cycle after core Snowflake steps."""
    
    def __init__(self, snowflake_workflow: SnowflakeWorkflow):
        self.workflow = snowflake_workflow
        self.agent = snowflake_workflow.agent
    
    def analyze_story(self, story: Story) -> str:
        """Analyze complete story for consistency and completeness."""
        story_context = story.get_story_context(up_to_step=9)
        return self.agent.analyze_story(story_context)
    
    def identify_scenes_needing_improvement(self, story: Story, analysis_data: dict) -> List[int]:
        """Extract scene numbers that need improvement from analysis data."""
        scene_numbers = set()
        
        # Get scenes from scene-specific recommendations
        scene_improvements = analysis_data.get("recommendations", {}).get("scene_improvements", [])
        for improvement in scene_improvements:
            scene_num = improvement.get("scene_number")
            if scene_num and isinstance(scene_num, int):
                scene_numbers.add(scene_num)
        
        # If no scene-specific recommendations, look for scene numbers in general issues
        if not scene_numbers:
            import re
            recommendations = analysis_data.get("recommendations", {})
            high_priority = recommendations.get("high_priority", [])
            medium_priority = recommendations.get("medium_priority", [])
            
            # Look for "Scene N" patterns in issues
            for issue in high_priority + medium_priority:
                scene_matches = re.findall(r'Scene (\d+)', issue)
                for match in scene_matches:
                    scene_numbers.add(int(match))
                
                # Look for character names (POV characters) in issues
                try:
                    scene_list = self.workflow.get_scene_list(story)
                    for scene in scene_list:
                        pov = scene.get("pov_character", "")
                        scene_num = scene.get("scene_number")
                        if pov and pov in issue and scene_num and isinstance(scene_num, int):
                            scene_numbers.add(scene_num)
                except Exception:
                    pass  # Skip if scene list can't be loaded
        
        return sorted(list(scene_numbers))
    
    def improve_scenes(self, story: Story, scene_numbers: List[int], analysis_data: dict = None) -> Tuple[int, List[str]]:
        """
        Improve multiple scenes based on analysis recommendations.
        
        Returns:
            (improved_count, error_messages)
        """
        improved_count = 0
        errors = []
        
        # Get current scene expansions
        step9_content = story.get_step_content(9)
        if not step9_content:
            return 0, ["No Step 9 content found"]
            
        try:
            current_expansions = json.loads(step9_content)
        except json.JSONDecodeError as e:
            return 0, [f"Could not parse Step 9 content: {e}"]
        
        # Get scene list for context
        try:
            scene_list = self.workflow.get_scene_list(story)
        except Exception as e:
            return 0, [f"Could not load scene list: {e}"]
        
        for scene_num in scene_numbers:
            try:
                scene_key = f"scene_{scene_num}"
                if scene_key not in current_expansions:
                    errors.append(f"Scene {scene_num} not found in expansions")
                    continue
                
                # Generate improvement guidance for this scene
                improvement_guidance = self._generate_improvement_guidance(
                    scene_num, scene_list, analysis_data
                )
                
                # Improve the scene
                improved_scene = self.workflow.improve_scene(story, scene_num, improvement_guidance)
                
                # Parse and update
                try:
                    improved_scene_data = json.loads(improved_scene)
                    current_expansions[scene_key] = improved_scene_data
                    improved_count += 1
                except json.JSONDecodeError as e:
                    errors.append(f"Could not parse improved Scene {scene_num}: {e}")
                    
            except Exception as e:
                errors.append(f"Error improving Scene {scene_num}: {e}")
        
        # Save updated scenes if any were improved
        if improved_count > 0:
            try:
                story.set_step_content(9, json.dumps(current_expansions, indent=2))
                story.save()
            except Exception as e:
                errors.append(f"Error saving improvements: {e}")
                return 0, errors
        
        return improved_count, errors
    
    def _generate_improvement_guidance(self, scene_num: int, scene_list: List[dict], analysis_data: dict = None) -> str:
        """Generate specific improvement guidance for a scene."""
        # Find scene data
        scene_data = None
        for scene in scene_list:
            if scene.get("scene_number") == scene_num:
                scene_data = scene
                break
        
        if not scene_data:
            return "Enhance character development, emotional depth, and concrete story details"
        
        pov = scene_data.get("pov_character", "")
        scene_description = scene_data.get("scene_description", "")
        
        scene_issues = []
        general_issues = []
        
        if analysis_data:
            recommendations = analysis_data.get("recommendations", {})
            high_priority = recommendations.get("high_priority", [])
            medium_priority = recommendations.get("medium_priority", [])
            
            for issue in high_priority + medium_priority:
                # Check if this issue is specifically relevant to this scene
                if f"Scene {scene_num}" in issue:
                    scene_issues.append(f"SPECIFIC: {issue}")
                elif pov and pov in issue:
                    scene_issues.append(f"CHARACTER ({pov}): {issue}")
                else:
                    # Check if issue relates to scene content/themes
                    issue_lower = issue.lower()
                    scene_desc_lower = scene_description.lower()
                    
                    # Look for thematic connections
                    if any(keyword in issue_lower and keyword in scene_desc_lower 
                           for keyword in ['artifact', 'magic', 'resistance', 'defeat', 'resolution', 'recovery']):
                        general_issues.append(f"THEMATIC: {issue}")
                    elif 'internal conflict' in issue_lower and pov:
                        general_issues.append(f"GENERAL: {issue}")
        
        # Combine specific and general issues
        all_issues = scene_issues + general_issues[:2]  # Limit general issues
        
        # If no specific issues, use general improvement guidance
        if not all_issues:
            return "Enhance character development, emotional depth, and concrete story details based on the scene's role in the overall story"
        
        return "; ".join(all_issues)


class StepProgression:
    """Handles the logic for advancing between Snowflake Method steps"""

    def __init__(self, workflow: SnowflakeWorkflow):
        self.workflow = workflow

    def advance_step(self, story: Story) -> Tuple[bool, str, Optional[str]]:
        """
        Advance story to next step.

        Returns:
            (success, message, generated_content)
        """
        current_step = story.get_current_step()
        next_step = current_step + 1

        # Check if we can advance
        if not self.workflow.can_advance(story, next_step):
            return (
                False,
                f"Cannot advance to step {next_step}. Complete step {current_step} first.",
                None,
            )

        try:
            if current_step == 1 and next_step == 2:
                content = self.workflow.expand_to_paragraph(story)
                return True, "Generated paragraph expansion", content

            elif current_step == 2 and next_step == 3:
                content = self.workflow.extract_characters(story)
                return True, "Generated character summaries", content

            elif current_step == 3 and next_step == 4:
                content = self.workflow.expand_to_plot(story)
                return True, "Generated plot summary", content

            elif current_step == 4 and next_step == 5:
                content = self.workflow.generate_character_synopses(story)
                return True, "Generated character synopses", content

            elif current_step == 5 and next_step == 6:
                content = self.workflow.expand_to_detailed_plot(story)
                return True, "Generated detailed plot synopsis", content

            elif current_step == 6 and next_step == 7:
                # Step 7 is special - we generate individual character charts
                # Return a special marker to indicate this needs special handling
                return (
                    True,
                    "Ready for character chart generation",
                    "INDIVIDUAL_CHARACTERS",
                )

            elif current_step == 7 and next_step == 8:
                content = self.workflow.generate_scene_breakdown(story)
                return True, "Generated scene breakdown", content

            elif current_step == 8 and next_step == 9:
                # Step 9 is special - we expand individual scenes
                # Return a special marker to indicate this needs special handling
                return (
                    True,
                    "Ready for scene expansion",
                    "INDIVIDUAL_SCENES",
                )

            elif current_step == 9 and next_step == 10:
                # Step 9 is the end of the Snowflake Method
                # Step 10 represents "ready for writing"
                return (
                    True,
                    "Snowflake Method complete - story ready for revision and writing",
                    "SNOWFLAKE_COMPLETE",
                )

            else:
                return (
                    False,
                    f"Step {current_step} -> {next_step} expansion not yet implemented.",
                    None,
                )

        except Exception as e:
            return False, f"Error generating content: {e}", None

    def accept_step_content(self, story: Story, content: str) -> None:
        """Accept and save the generated content for the next step"""
        next_step = story.get_current_step() + 1
        story.set_step_content(next_step, content)
        story.save()
