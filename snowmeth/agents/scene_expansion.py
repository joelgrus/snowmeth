"""Agent for Step 9: Expand individual scenes into detailed mini-outlines."""

import json
import random
import dspy
from typing import List
from pydantic import BaseModel, Field
from .shared_models import create_typed_refiner


class DetailedSceneExpansion(BaseModel):
    """Detailed scene expansion model for Step 9"""

    scene_number: int = Field(description="Scene number")
    title: str = Field(description="Compelling, specific scene title")
    pov_character: str = Field(description="Point of view character name")
    setting: str = Field(
        description="Detailed description of where and when - include sensory details, time of day, weather, atmosphere"
    )
    scene_goal: str = Field(
        description="Specific story function this scene serves - what plot/character development happens"
    )
    character_goal: str = Field(
        description="Concrete, specific goal the POV character pursues in this scene"
    )
    character_motivation: str = Field(
        description="Deep emotional/psychological reasons driving the character - connect to their backstory and arc"
    )
    obstacles: List[str] = Field(
        description="List 2-4 specific, concrete obstacles - people, events, internal conflicts"
    )
    conflict_type: str = Field(
        description="Describe the specific tension - internal struggle, interpersonal conflict, external threat"
    )
    key_beats: List[str] = Field(
        description="List 4-6 specific story moments with concrete actions, dialogue snippets, or emotional beats"
    )
    emotional_arc: str = Field(
        description="Specific emotional journey from opening feeling to closing feeling with turning points"
    )
    scene_outcome: str = Field(
        description="Concrete changes - what is different at scene end vs beginning"
    )
    subplot_elements: List[str] = Field(
        description="Specific subplot threads advanced - name the subplot and how it progresses"
    )
    character_relationships: str = Field(
        description="Specific relationship changes or developments with named characters"
    )
    foreshadowing: str = Field(
        description="Specific hints, symbols, or setup for future plot points"
    )
    estimated_pages: int = Field(description="Estimated page count for this scene")


class SceneExpansionGenerator(dspy.Signature):
    """Expand individual scenes into detailed, specific mini-outlines with concrete character goals, conflicts, and story beats"""

    story_context: str = dspy.InputField(
        desc="Full story context including all previous steps, character information, and plot details"
    )
    scene_info: str = dspy.InputField(
        desc="Information about the specific scene to expand, including scene number, POV character, description, and estimated pages"
    )
    scene_expansion: DetailedSceneExpansion = dspy.OutputField(
        desc="Create a detailed, specific scene expansion. Be concrete and specific, not generic. Include actual dialogue snippets, specific actions, and vivid details. Write as if creating a detailed scene outline for a professional novelist."
    )


class SceneImprover(dspy.Signature):
    """Improve a specific scene based on targeted feedback and analysis issues"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps, character information, and plot details"
    )
    scene_info = dspy.InputField(
        desc="Information about the specific scene to improve, including scene number, POV character, description, and estimated pages"
    )
    current_expansion = dspy.InputField(
        desc="Current scene expansion that needs improvement"
    )
    improvement_guidance = dspy.InputField(
        desc="Specific issues to address and improvements to make based on story analysis"
    )
    improved_scene: DetailedSceneExpansion = dspy.OutputField(
        desc="Improve the scene expansion based on the guidance provided. CRITICAL RULES: 1) DO NOT change the title unless the improvement_guidance specifically mentions title issues or the current title is clearly a placeholder (contains 'Placeholder' or 'Scene N'). Keep existing titles unless there is a compelling story reason to change them. 2) Focus improvements on content: character_motivation, key_beats, emotional_arc, scene_goal, obstacles, and other story elements. 3) Address the specific issues in improvement_guidance through content improvements, not title changes."
    )


class SceneExpansionAgent(dspy.Module):
    """Agent for expanding scenes into detailed mini-outlines (Step 9)."""

    def __init__(self):
        super().__init__()
        self.scene_expander = dspy.Predict(SceneExpansionGenerator)
        self.scene_improver = dspy.Predict(SceneImprover)
        # Create typed refiner for DetailedSceneExpansion
        SceneRefiner = create_typed_refiner(DetailedSceneExpansion, "scene expansion")
        self.refiner = dspy.Predict(SceneRefiner)

    def __call__(self, story_context: str, scene_info: str) -> str:
        """Expand a single scene into detailed mini-outline.

        Args:
            story_context: Full story context including all previous steps
            scene_info: Information about the specific scene to expand

        Returns:
            JSON string containing detailed scene expansion
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_expander(
            story_context=unique_context, scene_info=scene_info
        )

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.scene_expansion.dict(), indent=2)

    def improve_scene(
        self,
        story_context: str,
        scene_info: str,
        current_expansion: str,
        improvement_guidance: str,
    ) -> str:
        """Improve a specific scene with targeted feedback.

        Args:
            story_context: Full story context
            scene_info: Information about the scene
            current_expansion: Current scene expansion JSON
            improvement_guidance: Specific improvements to make

        Returns:
            Improved scene expansion JSON
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_improver(
            story_context=unique_context,
            scene_info=scene_info,
            current_expansion=current_expansion,
            improvement_guidance=improvement_guidance,
        )

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.improved_scene.dict(), indent=2)

    def refine(
        self,
        current_content: str,
        instructions: str,
        story_context: str,
        scene_info: str = "",
    ) -> str:
        """Refine scene expansion with specific instructions.

        Args:
            current_content: Current scene expansion JSON
            instructions: Specific refinement instructions
            story_context: Full story context
            scene_info: Optional scene information

        Returns:
            Refined scene expansion JSON
        """
        # If we have improvement guidance format, use the scene improver
        if "improvement_guidance" in instructions or "specific issues" in instructions:
            return self.improve_scene(
                story_context=story_context,
                scene_info=scene_info,
                current_expansion=current_content,
                improvement_guidance=instructions,
            )

        # Otherwise use typed refiner
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        
        result = self.refiner(
            current_content=current_content,
            story_context=unique_context,
            refinement_instructions=instructions,
        )

        # The typed refiner returns a structured DetailedSceneExpansion object
        return json.dumps(result.refined_output.dict(), indent=2)
