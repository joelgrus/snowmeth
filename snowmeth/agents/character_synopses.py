"""Agent for Step 5: Generate character synopses from each character's point of view."""

import json
import random
import dspy
from typing import Dict
from pydantic import BaseModel, Field
from .base import BaseAgent, clean_json_markdown
from .shared_models import ContentRefiner


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


class CharacterSynopsesAgent(BaseAgent):
    """Agent for generating character synopses from each character's POV (Step 5)."""
    
    def __init__(self, model_name: str = "default"):
        super().__init__(model_name)
        self.synopsis_generator = dspy.ChainOfThought(CharacterSynopsisGenerator)
        self.refiner = dspy.ChainOfThought(ContentRefiner)
    
    def generate(self, story_context: str) -> str:
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
    
    def refine(self, current_content: str, instructions: str, story_context: str) -> str:
        """Refine character synopses with specific instructions.
        
        Args:
            current_content: Current character synopses JSON
            instructions: Specific refinement instructions
            story_context: Full story context
            
        Returns:
            Refined character synopses JSON
        """
        # Parse the current JSON content
        try:
            current_synopses = json.loads(clean_json_markdown(current_content))
        except json.JSONDecodeError:
            # If parsing fails, treat as plain text
            current_synopses = current_content
        
        # Convert to string representation for refinement
        synopses_text = json.dumps(current_synopses, ensure_ascii=False, indent=2) if isinstance(current_synopses, dict) else current_content
        
        result = self.refiner(
            current_content=synopses_text,
            content_type="character synopses",
            story_context=story_context,
            refinement_instructions=instructions,
        )
        
        # Try to parse the refined content as JSON
        refined_content = result.refined_content
        try:
            # Clean and parse JSON
            cleaned_content = clean_json_markdown(refined_content)
            refined_synopses = json.loads(cleaned_content)
            return json.dumps(refined_synopses, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            # If it's not valid JSON, return as is
            return refined_content