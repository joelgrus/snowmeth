"""Shared models and signatures used across multiple Snowflake Method steps."""

import dspy


def clean_json_markdown(content: str) -> str:
    """Clean up potential markdown formatting from JSON content."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.endswith("```"):
        content = content[:-3]  # Remove ```
    return content.strip()


class ContentRefiner(dspy.Signature):
    """Refine any story content based on specific instructions"""

    current_content = dspy.InputField(desc="The current content to refine")
    content_type = dspy.InputField(
        desc="Type of content: sentence, paragraph, character, etc."
    )
    story_context = dspy.InputField(
        desc="Story context including original idea and previous steps"
    )
    refinement_instructions = dspy.InputField(
        desc="Specific instructions for how to refine the content"
    )
    refined_content = dspy.OutputField(
        desc="The content refined according to the instructions while maintaining consistency with the story context"
    )