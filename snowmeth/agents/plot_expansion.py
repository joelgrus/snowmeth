"""Agent for Step 4: Expand the paragraph summary into a detailed one-page plot summary."""

import dspy
import random
from .base import BaseAgent
from .shared_models import ContentRefiner


class PlotExpander(dspy.Signature):
    """Expand the paragraph summary into a detailed one-page plot summary"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, and character summaries"
    )
    plot_summary = dspy.OutputField(
        desc="A detailed one-page plot summary (400-500 words) that expands the paragraph into a complete plot structure. Develop the story's progression from beginning to end, showing key plot points and how character arcs integrate with the story. Maintain consistency with established characters and their motivations. Use whatever story structure works best for this particular narrative."
    )


class PlotExpansionAgent(BaseAgent):
    """Agent for expanding paragraph summary to detailed plot (Step 4)."""
    
    def __init__(self, model_name: str = "default"):
        super().__init__(model_name)
        self.plot_expander = dspy.ChainOfThought(PlotExpander)
        self.refiner = dspy.ChainOfThought(ContentRefiner)
    
    def generate(self, story_context: str) -> str:
        """Expand story context into detailed one-page plot summary.
        
        Args:
            story_context: Full story context including sentence, paragraph, and character summaries
            
        Returns:
            Detailed plot summary (400-500 words)
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.plot_expander(story_context=unique_context)
        return result.plot_summary
    
    def refine(self, current_content: str, instructions: str, story_context: str) -> str:
        """Refine the plot summary with specific instructions.
        
        Args:
            current_content: Current plot summary to refine
            instructions: Specific refinement instructions
            story_context: Full story context
            
        Returns:
            Refined plot summary
        """
        result = self.refiner(
            current_content=current_content,
            content_type="plot summary",
            story_context=story_context,
            refinement_instructions=instructions,
        )
        return result.refined_content