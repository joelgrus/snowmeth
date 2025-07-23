"""Step 1: One-sentence summary generation for the Snowflake Method."""

import dspy


class SentenceGenerator(dspy.Signature):
    """Generate a one-sentence summary for a novel based on a story idea"""

    story_idea = dspy.InputField(desc="The basic story idea or concept")
    sentence = dspy.OutputField(desc="A compelling one-sentence summary of the novel")


class SentenceSummaryAgent(dspy.Module):
    """Agent for generating one-sentence story summaries (Step 1)."""
    
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(SentenceGenerator)
    
    def __call__(self, story_idea: str) -> str:
        """Generate a one-sentence summary from a story idea.
        
        Args:
            story_idea: The basic story idea or concept
            
        Returns:
            A compelling one-sentence summary of the novel
        """
        result = self.generator(story_idea=story_idea)
        return result.sentence