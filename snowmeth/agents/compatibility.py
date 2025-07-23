"""Compatibility wrapper to maintain the original SnowflakeAgent API."""

import dspy
import json
import random
from typing import AsyncGenerator
from ..config import LLMConfig
from .sentence_summary import SentenceSummaryAgent
from .paragraph_expansion import ParagraphExpansionAgent
from .character_extraction import CharacterExtractionAgent
from .plot_expansion import PlotExpansionAgent
from .character_synopses import CharacterSynopsesAgent
from .detailed_plot import DetailedPlotAgent
from .character_charts import CharacterChartsAgent
from .scene_breakdown import SceneBreakdownAgent
from .scene_expansion import SceneExpansionAgent
from .story_analyzer import StoryAnalyzerAgent
from .chapter_writer import ChapterWriterAgent
from .shared_models import ContentRefiner


class SnowflakeAgent:
    """Compatibility wrapper for the original SnowflakeAgent API."""
    
    def __init__(self):
        """Initialize the agent with all step agents."""
        # Configure DSPy with LLM
        llm_config = LLMConfig()
        default_model = llm_config.get_model("default")
        lm = llm_config.create_lm(default_model)
        dspy.configure(lm=lm)
        
        # Initialize all step agents
        self.sentence_agent = SentenceSummaryAgent()
        self.paragraph_agent = ParagraphExpansionAgent()
        self.character_agent = CharacterExtractionAgent()
        self.plot_agent = PlotExpansionAgent()
        self.synopses_agent = CharacterSynopsesAgent()
        self.detailed_plot_agent = DetailedPlotAgent()
        self.charts_agent = CharacterChartsAgent()
        self.breakdown_agent = SceneBreakdownAgent()
        self.expansion_agent = SceneExpansionAgent()
        self.analyzer_agent = StoryAnalyzerAgent()
        self.writer_agent = ChapterWriterAgent()
        
        # For content refinement
        self.refiner = None  # Will be initialized on first use
    
    def _ensure_refiner(self):
        """Lazy initialization of content refiner."""
        if self.refiner is None:
            import dspy
            self.refiner = dspy.ChainOfThought(ContentRefiner)
    
    def generate_sentence(self, story_idea: str) -> str:
        """Generate Step 1: One-sentence summary."""
        return self.sentence_agent(story_idea)
    
    def expand_to_paragraph(self, sentence_summary: str, story_idea: str) -> str:
        """Generate Step 2: Paragraph expansion."""
        return self.paragraph_agent(sentence_summary, story_idea)
    
    def extract_characters(self, story_context: str) -> str:
        """Generate Step 3: Character extraction."""
        return self.character_agent(story_context)
    
    def expand_to_plot(self, story_context: str) -> str:
        """Generate Step 4: Plot expansion."""
        return self.plot_agent(story_context)
    
    def generate_character_synopses(self, story_context: str) -> str:
        """Generate Step 5: Character synopses."""
        return self.synopses_agent(story_context)
    
    def expand_to_detailed_plot(self, story_context: str) -> str:
        """Generate Step 6: Detailed plot."""
        return self.detailed_plot_agent(story_context)
    
    def generate_detailed_character_chart(self, story_context: str, character_name: str = None) -> str:
        """Generate Step 7: Character charts."""
        if character_name:
            return self.charts_agent(story_context, character_name)
        else:
            return self.charts_agent(story_context)
    
    def generate_scene_breakdown(self, story_context: str) -> str:
        """Generate Step 8: Scene breakdown."""
        return self.breakdown_agent(story_context)
    
    def expand_scene(self, story_context: str, scene_info: str) -> str:
        """Generate Step 9: Scene expansion."""
        return self.expansion_agent(story_context, scene_info)
    
    def generate_chapter_prose(self, story_context: str, scene_expansion: str, chapter_number: int, previous_chapters: str = "", style_instructions: str = "") -> str:
        """Generate Step 10: Chapter prose."""
        return self.writer_agent.generate_chapter_prose(story_context, scene_expansion, chapter_number, previous_chapters, style_instructions)
    
    def refine_chapter_prose(self, chapter_content: str, refinement_instructions: str, story_context: str, scene_expansion: str, style_instructions: str = "") -> str:
        """Refine chapter prose."""
        return self.writer_agent.refine_chapter_prose(chapter_content, refinement_instructions, story_context, scene_expansion, style_instructions)
    
    def analyze_story(self, story_context: str) -> str:
        """Analyze story."""
        return self.analyzer_agent(story_context)
    
    def refine_content(self, current_content: str, content_type: str, story_context: str, refinement_instructions: str) -> str:
        """Refine content based on instructions."""
        self._ensure_refiner()
        
        # Add randomization to avoid caching
        random_context = f"{story_context}\n\nRandom seed: {random.randint(1, 10000)}"
        
        result = self.refiner(
            current_content=current_content,
            content_type=content_type,
            story_context=random_context,
            refinement_instructions=refinement_instructions
        )
        return result.refined_content
    
    def improve_scene(self, story_context: str, scene_info: str, current_expansion: str, improvement_guidance: str) -> str:
        """Improve a specific scene."""
        improved = self.expansion_agent.improve_scene(story_context, scene_info, current_expansion, improvement_guidance)
        return json.dumps(improved, indent=2)
    
    async def stream_chapter_generation(self, story_context: str, scene_expansion: str, chapter_number: int, previous_chapters: str = "", style_instructions: str = "") -> AsyncGenerator[str, None]:
        """Stream chapter generation."""
        async for chunk in self.writer_agent.stream_chapter_generation(
            story_context, scene_expansion, chapter_number, previous_chapters, style_instructions
        ):
            yield chunk