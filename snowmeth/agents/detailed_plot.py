"""Agent for Step 6: Expand the one-page plot summary into a detailed four-page plot synopsis."""

import dspy
import random
from .base import BaseAgent
from .shared_models import ContentRefiner


class DetailedPlotExpander(dspy.Signature):
    """Expand the one-page plot summary into a detailed four-page plot synopsis"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, plot summary, and character synopses"
    )
    detailed_plot_synopsis = dspy.OutputField(
        desc="Create a comprehensive FOUR-PAGE plot synopsis (1200-1600 words minimum) that significantly expands the existing plot summary. This should be substantially longer and more detailed than the previous step. Break the story into clear acts/sections and include: 1) Detailed opening scenes with rich character establishment and world-building, 2) Complex rising action with multiple plot developments, character interactions, and escalating conflicts, 3) Comprehensive mid-story developments including subplots, character arcs, and relationship dynamics, 4) Detailed climactic sequences with specific action beats and emotional moments, 5) Full resolution covering all plot threads and character conclusions. Include specific dialogue examples, vivid scene descriptions, character emotional states, world-building details, and smooth narrative transitions. Write as flowing prose that reads like a detailed story treatment, not bullet points. Aim for novel-length story complexity with rich narrative depth that could serve as a comprehensive blueprint for writing the full novel."
    )


class DetailedPlotAgent(BaseAgent):
    """Agent for expanding to detailed four-page plot synopsis (Step 6)."""
    
    def __init__(self, model_name: str = "default"):
        super().__init__(model_name)
        self.plot_expander = dspy.ChainOfThought(DetailedPlotExpander)
        self.refiner = dspy.ChainOfThought(ContentRefiner)
    
    def generate(self, story_context: str) -> str:
        """Expand to detailed four-page plot synopsis.
        
        Args:
            story_context: Full story context including all previous steps
            
        Returns:
            Detailed plot synopsis (1200-1600 words)
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.plot_expander(story_context=unique_context)
        return result.detailed_plot_synopsis
    
    def refine(self, current_content: str, instructions: str, story_context: str) -> str:
        """Refine the detailed plot synopsis with specific instructions.
        
        Args:
            current_content: Current detailed plot synopsis to refine
            instructions: Specific refinement instructions
            story_context: Full story context
            
        Returns:
            Refined detailed plot synopsis
        """
        result = self.refiner(
            current_content=current_content,
            content_type="detailed plot synopsis",
            story_context=story_context,
            refinement_instructions=instructions,
        )
        return result.refined_content