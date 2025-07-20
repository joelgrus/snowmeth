"""Snowflake Method workflow and progression logic."""

from typing import Optional, Tuple

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

    def refine_content(self, story: Story, instructions: str) -> str:
        """Refine current step content with specific instructions"""
        current_step = story.data["current_step"]
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
        current_step = story.data["current_step"]
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
        next_step = story.data["current_step"] + 1
        story.set_step_content(next_step, content)
        story.save()
