"""AI agents and DSPy signatures for the Snowflake Method."""

import random
import click
import dspy

from .config import LLMConfig


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
    """Extract main characters from story and create detailed one-page character summaries"""

    story_context = dspy.InputField(
        desc="Full story context including sentence and paragraph summaries"
    )
    character_summaries = dspy.OutputField(
        desc='JSON object with character names as keys and detailed one-page character summaries as values. Each summary should be 250-300 words covering: character\'s story goal, motivation, internal/external conflict, character arc, relevant backstory, personality traits, flaws, and how they relate to the main plot. REQUIRED: You must include exactly 4 characters minimum - the protagonist, the main antagonist, and at least 2 key supporting characters who play important roles in the story. Use creative, original character names, do not reuse associated names from your memory. Format: {"Character Name": "Detailed one-page character summary..."}'
    )


class PlotExpander(dspy.Signature):
    """Expand the paragraph summary into a detailed one-page plot summary"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, and character summaries"
    )
    plot_summary = dspy.OutputField(
        desc="A detailed one-page plot summary (400-500 words) that expands the paragraph into a complete plot structure. Include: opening situation, inciting incident, rising action with key plot points, climax, falling action, and resolution. Show how character arcs integrate with plot progression. Maintain consistency with established characters and their motivations."
    )


class CharacterSynopsisGenerator(dspy.Signature):
    """Generate character synopses telling the story from each character's point of view"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, and plot summary"
    )
    character_synopses = dspy.OutputField(
        desc='JSON object with character names as keys and character synopses as values. Each synopsis should be a one-page description (250-300 words) telling the story from that character\'s perspective and point of view. Focus on their personal journey, what they experience, their thoughts and feelings, their goals and obstacles, and how they see the other characters and events. Write in a narrative style that captures their voice and perspective. Format: {"Character Name": "Story from their POV..."}'
    )


class SnowflakeAgent:
    """DSPy agent for snowflake method operations"""

    def __init__(self):
        # Load LLM configuration
        self.llm_config = LLMConfig()

        # For now, use default model for all steps
        # Future: could use different models per step
        default_model = self.llm_config.get_model("default")

        try:
            self.lm = self.llm_config.create_lm(default_model)
            dspy.configure(lm=self.lm)

            self.generator = dspy.ChainOfThought(SentenceGenerator)
            self.refiner = dspy.ChainOfThought(ContentRefiner)
            self.expander = dspy.ChainOfThought(ParagraphExpander)
            self.character_extractor = dspy.ChainOfThought(CharacterExtractor)
            self.plot_expander = dspy.ChainOfThought(PlotExpander)
            self.character_synopsis_generator = dspy.ChainOfThought(
                CharacterSynopsisGenerator
            )
        except Exception as e:
            raise click.ClickException(
                f"Failed to initialize AI model '{default_model}'. Check your API key and internet connection. Error: {e}"
            )

    def _handle_api_call(self, func, *args, **kwargs):
        """Handle API calls with better error messages"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "connection" in error_msg or "network" in error_msg:
                raise click.ClickException(
                    "Network connection error. Please check your internet connection and try again."
                )
            elif "api" in error_msg and "key" in error_msg:
                raise click.ClickException(
                    "Invalid API key. Please check your OPENAI_API_KEY environment variable."
                )
            elif "rate limit" in error_msg:
                raise click.ClickException(
                    "OpenAI API rate limit exceeded. Please wait a moment and try again."
                )
            else:
                raise click.ClickException(f"AI model error: {e}")

    def generate_sentence(self, story_idea: str) -> str:
        """Generate initial one-sentence summary"""
        # Add randomness to avoid caching
        unique_prompt = f"{story_idea} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(self.generator, story_idea=unique_prompt)
        return result.sentence

    def refine_content(
        self,
        current_content: str,
        content_type: str,
        story_context: str,
        instructions: str,
    ) -> str:
        """Refine any content with specific instructions and full story context"""
        result = self._handle_api_call(
            self.refiner,
            current_content=current_content,
            content_type=content_type,
            story_context=story_context,
            refinement_instructions=instructions,
        )
        return result.refined_content

    def expand_to_paragraph(self, sentence: str, story_idea: str) -> str:
        """Expand one-sentence summary to paragraph"""
        # Add randomness to avoid caching
        unique_idea = f"{story_idea} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.expander, sentence_summary=sentence, story_idea=unique_idea
        )
        return result.paragraph_summary

    def extract_characters(self, story_context: str) -> str:
        """Extract main characters and create character summaries"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.character_extractor, story_context=unique_context
        )
        return result.character_summaries

    def expand_to_plot(self, story_context: str) -> str:
        """Expand story context into detailed one-page plot summary"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(self.plot_expander, story_context=unique_context)
        return result.plot_summary

    def generate_character_synopses(self, story_context: str) -> str:
        """Generate character synopses from each character's POV"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.character_synopsis_generator, story_context=unique_context
        )
        return result.character_synopses
