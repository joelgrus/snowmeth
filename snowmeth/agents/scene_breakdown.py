"""Agent for Step 8: Break down the plot into individual scenes."""

import json
import random
import dspy
from typing import List
from pydantic import BaseModel, Field
from .shared_models import ContentRefiner


class SceneBreakdown(BaseModel):
    """Individual scene in a novel breakdown"""

    scene_number: int = Field(description="Scene number in sequence")
    pov_character: str = Field(description="Point of view character for this scene")
    scene_description: str = Field(
        description="2-3 sentences describing major events and character development"
    )
    estimated_pages: int = Field(
        description="Estimated page count - should be substantial (20-50 pages) for chapter-length scenes"
    )


class NovelSceneBreakdown(BaseModel):
    """Complete scene breakdown for a novel"""

    scenes: List[SceneBreakdown] = Field(description="List of all scenes in the novel")
    total_estimated_pages: int = Field(
        description="Total estimated pages for the complete novel"
    )


class SceneBreakdownGenerator(dspy.Signature):
    """Break down the four-page plot synopsis into individual chapter-length scenes for a novel"""

    story_context: str = dspy.InputField(
        desc="Full story context including all previous steps, especially the detailed four-page plot synopsis from Step 6"
    )
    scene_breakdown: NovelSceneBreakdown = dspy.OutputField(
        desc="Break down the plot synopsis into substantial chapter-length scenes. Each scene should be a major story section. The number of scenes should be determined by the story's natural structure, but should be at least 20. Scenes should typically be 10-20 pages each to create a full novel (200-500 pages total)."
    )


class SceneBreakdownAgent(dspy.Module):
    """Agent for breaking down plot into scenes (Step 8)."""

    def __init__(self):
        super().__init__()
        self.breakdown_generator = dspy.ChainOfThought(SceneBreakdownGenerator)
        self.refiner = dspy.ChainOfThought(ContentRefiner)

    def __call__(self, story_context: str) -> str:
        """Generate scene breakdown from four-page plot synopsis.

        Args:
            story_context: Full story context including all previous steps

        Returns:
            JSON string containing list of scenes
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.breakdown_generator(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        scenes_list = [scene.dict() for scene in result.scene_breakdown.scenes]
        return json.dumps(scenes_list, indent=2)

    def refine(
        self, current_content: str, instructions: str, story_context: str
    ) -> str:
        """Refine scene breakdown with specific instructions.

        Args:
            current_content: Current scene breakdown JSON
            instructions: Specific refinement instructions
            story_context: Full story context

        Returns:
            Refined scene breakdown JSON
        """
        result = self.refiner(
            current_content=current_content,
            content_type="scene breakdown",
            story_context=story_context,
            refinement_instructions=instructions,
        )

        # Ensure the result is valid JSON
        try:
            # Try to parse and re-format as JSON
            refined_data = json.loads(result.refined_content)
            return json.dumps(refined_data, indent=2)
        except json.JSONDecodeError:
            # If parsing fails, return as is
            return result.refined_content
