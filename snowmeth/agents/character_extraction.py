"""Step 3: Character extraction and summary for the Snowflake Method."""

import dspy
from typing import Dict
from pydantic import BaseModel, Field


class CharacterSummaries(BaseModel):
    """Structured character summaries model"""

    characters: Dict[str, str] = Field(
        description="Dictionary with character names as keys and detailed character summaries as values"
    )


class CharacterExtractor(dspy.Signature):
    """Extract main characters from story and create detailed one-page character summaries"""

    story_context: str = dspy.InputField(
        desc="Full story context including sentence and paragraph summaries"
    )
    characters: CharacterSummaries = dspy.OutputField(
        desc="Character summaries as a JSON object with names as keys and detailed summaries as values. Each summary should be 250-300 words covering: character's story goal, motivation, internal/external conflict, character arc, relevant backstory, personality traits, flaws, and how they relate to the main plot. REQUIRED: You must include exactly 4 characters minimum - the protagonist, the main antagonist, and at least 2 key supporting characters who play important roles in the story. Use appropriate character names that fit the story's setting and genre."
    )


class CharacterExtractionAgent(dspy.Module):
    """Agent for extracting and summarizing characters (Step 3)."""
    
    def __init__(self):
        super().__init__()
        self.extractor = dspy.ChainOfThought(CharacterExtractor)
    
    def __call__(self, story_context: str) -> str:
        """Extract main characters and create character summaries.
        
        Args:
            story_context: Full story context including sentence and paragraph summaries
            
        Returns:
            JSON string containing character summaries dictionary
        """
        import json
        import random
        
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.extractor(story_context=unique_context)
        
        # The structured output should give us a CharacterSummaries object
        # result.characters is the CharacterSummaries model instance
        # result.characters.characters is the dict we want
        character_dict = result.characters.characters
        
        # Ensure we return valid JSON
        return json.dumps(character_dict, ensure_ascii=False, indent=2)
    
    def refine(self, current_content: str, instructions: str, story_context: str) -> str:
        """Refine character summaries with specific instructions.
        
        Args:
            current_content: Current character summaries JSON
            instructions: Specific refinement instructions
            story_context: Full story context
            
        Returns:
            Refined character summaries JSON
        """
        from .shared_models import ContentRefiner, clean_json_markdown
        import json
        
        refiner = dspy.ChainOfThought(ContentRefiner)
        
        # Parse the current JSON content
        try:
            current_characters = json.loads(clean_json_markdown(current_content))
        except json.JSONDecodeError:
            # If parsing fails, treat as plain text
            current_characters = current_content
        
        # Convert to string representation for refinement
        characters_text = json.dumps(current_characters, ensure_ascii=False, indent=2) if isinstance(current_characters, dict) else current_content
        
        result = refiner(
            current_content=characters_text,
            content_type="character summaries",
            story_context=story_context,
            refinement_instructions=instructions,
        )
        
        # Try to parse the refined content as JSON
        refined_content = result.refined_content
        try:
            # Clean and parse JSON
            cleaned_content = clean_json_markdown(refined_content)
            refined_characters = json.loads(cleaned_content)
            return json.dumps(refined_characters, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            # If it's not valid JSON, return as is
            return refined_content