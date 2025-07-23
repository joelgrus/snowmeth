"""Agent for Step 5: Generate character synopses from each character's point of view."""

import json
import random
import dspy
from typing import Dict
from pydantic import BaseModel, Field
from .shared_models import create_typed_refiner


class CharacterSynopses(BaseModel):
    """Structured character synopses model"""

    character_synopses: Dict[str, str] = Field(
        description="Dictionary with character names as keys and character synopses as values"
    )


class CharacterSynopsisGenerator(dspy.Signature):
    """Generate character synopses telling the story from each character's point of view"""

    story_context: str = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, and plot summary"
    )
    synopses: CharacterSynopses = dspy.OutputField(
        desc="Character synopses as a JSON object with names as keys and synopses as values. Each synopsis should be a one-page description (250-300 words) telling the story from that character's perspective and point of view. Focus on their personal journey, what they experience, their thoughts and feelings, their goals and obstacles, and how they see the other characters and events. Write in a narrative style that captures their voice and perspective."
    )


class CharacterSynopsesAgent(dspy.Module):
    """Agent for generating character synopses from each character's POV (Step 5)."""

    def __init__(self):
        super().__init__()
        self.synopsis_generator = dspy.ChainOfThought(CharacterSynopsisGenerator)
        # Create typed refiner for CharacterSynopses
        SynopsesRefiner = create_typed_refiner(CharacterSynopses, "character synopses")
        self.refiner = dspy.ChainOfThought(SynopsesRefiner)

    def __call__(self, story_context: str) -> str:
        """Generate character synopses from each character's POV.

        Args:
            story_context: Full story context including all previous steps

        Returns:
            JSON string containing character synopses dictionary
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.synopsis_generator(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        character_synopses = result.synopses.character_synopses

        # Filter out entries with empty values
        filtered_synopses = {
            name: synopsis
            for name, synopsis in character_synopses.items()
            if synopsis and synopsis.strip()
        }

        return json.dumps(filtered_synopses, ensure_ascii=False, indent=2)

    def refine(
        self, current_content: str, instructions: str, story_context: str
    ) -> str:
        """Refine character synopses with specific instructions.

        Args:
            current_content: Current character synopses JSON
            instructions: Specific refinement instructions
            story_context: Full story context

        Returns:
            Refined character synopses JSON
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        
        result = self.refiner(
            current_content=current_content,
            story_context=unique_context,
            refinement_instructions=instructions,
        )

        # The typed refiner returns a structured CharacterSynopses object
        character_synopses = result.refined_output.character_synopses
        
        # Filter out entries with empty values
        filtered_synopses = {
            name: synopsis
            for name, synopsis in character_synopses.items()
            if synopsis and synopsis.strip()
        }

        return json.dumps(filtered_synopses, ensure_ascii=False, indent=2)
