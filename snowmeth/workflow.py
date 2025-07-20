"""Snowflake Method workflow and progression logic."""

from typing import Optional, Tuple, List
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

    def analyze_story(self, story: Story) -> str:
        """Analyze complete story for consistency and completeness for Step 9.5"""
        story_context = story.get_story_context(up_to_step=9)
        return self.agent.analyze_story(story_context)

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
