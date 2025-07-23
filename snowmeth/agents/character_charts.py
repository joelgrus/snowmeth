"""Agent for Step 7: Generate detailed character charts for each character."""

import dspy
import random
from .shared_models import ContentRefiner


class DetailedCharacterChartGenerator(dspy.Signature):
    """Generate a comprehensive character chart for a single character"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps and information about other characters"
    )
    character_name = dspy.InputField(
        desc="The name of the specific character to generate a detailed chart for"
    )
    character_chart = dspy.OutputField(
        desc="Create a comprehensive character chart that fully develops this character with rich, specific details. Provide: detailed physical appearance (height, build, distinctive features, scars, clothing, etc.), concrete personality traits and specific mannerisms, complete background story with key life events, clear motivations and goals, defined relationships with other characters, specific skills and abilities, detailed character arc showing how they change, particular fears and strengths, unique speech patterns or catchphrases, and meaningful possessions or symbols. Be creative and specific - invent concrete details that bring this character to life rather than describing what isn't known. Write as flowing, detailed prose that reads like a character bible entry. Use plain text without any markdown formatting - no asterisks, headers, or special symbols."
    )


class CharacterChartsAgent(dspy.Module):
    """Agent for generating detailed character charts (Step 7)."""

    def __init__(self):
        super().__init__()
        self.chart_generator = dspy.ChainOfThought(DetailedCharacterChartGenerator)
        self.refiner = dspy.ChainOfThought(ContentRefiner)

    def __call__(self, story_context: str, character_name: str) -> str:
        """Generate detailed character chart for a single character.

        Args:
            story_context: Full story context including all previous steps
            character_name: Name of the character to generate chart for

        Returns:
            Detailed character chart as prose text
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.chart_generator(
            story_context=unique_context,
            character_name=character_name,
        )
        return result.character_chart

    def refine(
        self,
        current_content: str,
        instructions: str,
        story_context: str,
        character_name: str,
    ) -> str:
        """Refine a character chart with specific instructions.

        Args:
            current_content: Current character chart to refine
            instructions: Specific refinement instructions
            story_context: Full story context
            character_name: Name of the character being refined

        Returns:
            Refined character chart
        """
        result = self.refiner(
            current_content=current_content,
            content_type=f"character chart for {character_name}",
            story_context=story_context,
            refinement_instructions=instructions,
        )
        return result.refined_content
