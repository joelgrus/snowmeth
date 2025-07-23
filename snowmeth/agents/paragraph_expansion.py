"""Step 2: Paragraph expansion for the Snowflake Method."""

import dspy


class ParagraphExpander(dspy.Signature):
    """Expand a one-sentence novel summary into a full paragraph"""

    sentence_summary = dspy.InputField(desc="The one-sentence summary to expand")
    story_idea = dspy.InputField(desc="The original story idea for context")
    paragraph = dspy.OutputField(
        desc="A compelling paragraph (3-5 sentences) that expands on the summary with more detail about the setup, conflict, and stakes"
    )


class ParagraphExpansionAgent(dspy.Module):
    """Agent for expanding sentence summary to paragraph (Step 2)."""
    
    def __init__(self):
        super().__init__()
        self.expander = dspy.ChainOfThought(ParagraphExpander)
    
    def __call__(self, sentence_summary: str, story_idea: str) -> str:
        """Expand a one-sentence summary into a full paragraph.
        
        Args:
            sentence_summary: The one-sentence summary to expand
            story_idea: The original story idea for context
            
        Returns:
            A compelling paragraph expanding on the summary
        """
        result = self.expander(
            sentence_summary=sentence_summary,
            story_idea=story_idea
        )
        return result.paragraph