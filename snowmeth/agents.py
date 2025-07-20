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


class DetailedPlotExpander(dspy.Signature):
    """Expand the one-page plot summary into a detailed four-page plot synopsis"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, plot summary, and character synopses"
    )
    detailed_plot_synopsis = dspy.OutputField(
        desc="A comprehensive four-page plot synopsis (6000-8000 words total) that expands the existing plot summary into extensive detail. Write as a flowing narrative covering the opening and setup, inciting incident and early conflict, rising action and character development, climax and major confrontation, falling action and immediate aftermath, and resolution and conclusion. Include detailed scene descriptions, character interactions and dialogue snippets, specific plot developments, emotional beats, world-building details, and smooth transitions between events. Maintain consistency with established characters and their motivations while adding rich narrative depth. Write in paragraph form without section headers."
    )


class DetailedCharacterChartGenerator(dspy.Signature):
    """Generate a comprehensive character chart for a single character"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps and information about other characters"
    )
    character_name = dspy.InputField(
        desc="The name of the specific character to generate a detailed chart for"
    )
    character_chart = dspy.OutputField(
        desc="A comprehensive character chart (800-1200 words) containing: Full name and any aliases, Age and birthdate, Physical description (height, build, hair, eyes, distinguishing features), Personality traits and quirks, Background and personal history, Family and relationships, Education and skills, Goals and motivations (both surface and deep), Internal and external conflicts, Character arc (how they change throughout the story), Fears and vulnerabilities, Strengths and talents, Speech patterns and mannerisms, Important possessions or symbols, Role in the story and relationships with other characters. Write in detailed prose form, not as a list or bullet points."
    )


class SceneBreakdownGenerator(dspy.Signature):
    """Break down the four-page plot synopsis into individual scenes for a novel"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps, especially the detailed four-page plot synopsis from Step 6"
    )
    scene_breakdown = dspy.OutputField(
        desc='JSON array of scene objects breaking down the four-page plot synopsis into individual scenes. Each scene should be an object with: "scene_number" (integer), "pov_character" (string - which character\'s point of view), "scene_description" (string - 2-3 sentences describing what happens in this scene), "estimated_pages" (integer - rough estimate of pages this scene might take, typically 8-20 pages for major scenes, 4-12 pages for smaller scenes). Aim for 15-25 scenes total to cover the full novel, targeting 250-400 total pages. Focus on key dramatic moments, character interactions, plot advancement, and emotional beats. Format: [{"scene_number": 1, "pov_character": "Character Name", "scene_description": "Description of what happens...", "estimated_pages": 12}, ...]'
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
            self.detailed_plot_expander = dspy.ChainOfThought(DetailedPlotExpander)
            self.detailed_character_chart_generator = dspy.ChainOfThought(
                DetailedCharacterChartGenerator
            )
            self.scene_breakdown_generator = dspy.ChainOfThought(
                SceneBreakdownGenerator
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

    def expand_to_detailed_plot(self, story_context: str) -> str:
        """Expand to detailed four-page plot synopsis for Step 6"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.detailed_plot_expander, story_context=unique_context
        )
        return result.detailed_plot_synopsis

    def generate_detailed_character_chart(
        self, story_context: str, character_name: str
    ) -> str:
        """Generate detailed character chart for a single character for Step 7"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.detailed_character_chart_generator,
            story_context=unique_context,
            character_name=character_name,
        )
        return result.character_chart

    def generate_scene_breakdown(self, story_context: str) -> str:
        """Generate scene breakdown from four-page plot synopsis for Step 8"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self._handle_api_call(
            self.scene_breakdown_generator, story_context=unique_context
        )
        return result.scene_breakdown
