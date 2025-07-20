"""AI agents and DSPy signatures for the Snowflake Method."""

import click
import dspy


class SentenceGenerator(dspy.Signature):
    """Generate a one-sentence summary for a novel based on a story idea"""

    story_idea = dspy.InputField(desc="The basic story idea or concept")
    sentence = dspy.OutputField(desc="A compelling one-sentence summary of the novel")


class ContentRefiner(dspy.Signature):
    """Refine any story content based on specific instructions"""

    current_content = dspy.InputField(desc="The current content to refine")
    content_type = dspy.InputField(
        desc="Type of content: sentence, paragraph, character, etc."
    )
    story_context = dspy.InputField(
        desc="Story context including original idea and previous steps"
    )
    refinement_instructions = dspy.InputField(
        desc="Specific instructions for how to refine the content"
    )
    refined_content = dspy.OutputField(
        desc="The content refined according to the instructions while maintaining consistency with the story context"
    )


class ParagraphExpander(dspy.Signature):
    """Expand a one-sentence novel summary into a full paragraph"""

    sentence_summary = dspy.InputField(desc="The one-sentence summary to expand")
    story_idea = dspy.InputField(desc="The original story idea for context")
    paragraph_summary = dspy.OutputField(
        desc="A full paragraph (4-5 sentences) expanding on the one-sentence summary, including key plot points, conflict, and stakes"
    )


class CharacterExtractor(dspy.Signature):
    """Extract main characters from story and create character summaries"""

    story_context = dspy.InputField(
        desc="Full story context including sentence and paragraph summaries"
    )
    character_summaries = dspy.OutputField(
        desc='JSON object with character names as keys and brief character summaries as values. Include protagonist, antagonist, and key supporting characters. Format: {"Character Name": "Brief character summary including role, motivation, and key traits"}'
    )


class SnowflakeAgent:
    """DSPy agent for snowflake method operations"""

    def __init__(self):
        # Configure OpenAI model
        try:
            self.lm = dspy.LM("openai/gpt-4o-mini")
            dspy.configure(lm=self.lm)

            self.generator = dspy.ChainOfThought(SentenceGenerator)
            self.refiner = dspy.ChainOfThought(ContentRefiner)
            self.expander = dspy.ChainOfThought(ParagraphExpander)
            self.character_extractor = dspy.ChainOfThought(CharacterExtractor)
        except Exception as e:
            raise click.ClickException(
                f"Failed to initialize AI model. Make sure OPENAI_API_KEY is set. Error: {e}"
            )

    def generate_sentence(self, story_idea: str) -> str:
        """Generate initial one-sentence summary"""
        result = self.generator(story_idea=story_idea)
        return result.sentence

    def refine_content(
        self,
        current_content: str,
        content_type: str,
        story_context: str,
        instructions: str,
    ) -> str:
        """Refine any content with specific instructions and full story context"""
        result = self.refiner(
            current_content=current_content,
            content_type=content_type,
            story_context=story_context,
            refinement_instructions=instructions,
        )
        return result.refined_content

    def expand_to_paragraph(self, sentence: str, story_idea: str) -> str:
        """Expand one-sentence summary to paragraph"""
        result = self.expander(sentence_summary=sentence, story_idea=story_idea)
        return result.paragraph_summary

    def extract_characters(self, story_context: str) -> str:
        """Extract main characters and create character summaries"""
        result = self.character_extractor(story_context=story_context)
        return result.character_summaries
