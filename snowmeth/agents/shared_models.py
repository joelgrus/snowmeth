"""Shared models and signatures used across multiple Snowflake Method steps."""

import dspy
from typing import TypeVar, Type
from pydantic import BaseModel


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


# Generic typed refiner
T = TypeVar('T', bound=BaseModel)


def create_typed_refiner(output_model: Type[T], content_description: str) -> Type[dspy.Signature]:
    """Create a typed refiner signature for a specific Pydantic model.
    
    Args:
        output_model: The Pydantic model class for the refined output
        content_description: Description of what type of content is being refined
    
    Returns:
        A DSPy signature class for refining content to the specified model
    """
    
    # Create the class dynamically with proper type annotations
    return type(
        f"TypedRefiner_{output_model.__name__}",
        (dspy.Signature,),
        {
            "__doc__": f"""Refine {content_description} based on specific instructions while maintaining proper structure.
            
            CRITICAL: Output must be valid, well-structured {content_description} that follows the required format.
            Apply the refinement instructions while preserving the essential content structure and completeness.
            """,
            "__annotations__": {
                "current_content": str,
                "story_context": str, 
                "refinement_instructions": str,
                "refined_output": output_model,
            },
            "current_content": dspy.InputField(desc=f"The current {content_description} to refine"),
            "story_context": dspy.InputField(
                desc="Story context including original idea and previous steps"
            ),
            "refinement_instructions": dspy.InputField(
                desc="Specific instructions for how to refine the content"
            ),
            "refined_output": dspy.OutputField(
                desc=f"The refined {content_description} with improvements applied while maintaining proper structure"
            ),
        }
    )
