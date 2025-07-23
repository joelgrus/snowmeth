"""Compatibility wrapper to maintain the original SnowflakeAgent API."""

import json
import random
from typing import AsyncGenerator
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
    
    def generate_step_1(self, story_idea: str) -> str:
        """Generate Step 1: One-sentence summary."""
        return self.sentence_agent.generate(story_idea)
    
    # Legacy method names for backward compatibility
    def generate_sentence(self, story_idea: str) -> str:
        """Legacy: Generate Step 1: One-sentence summary."""
        return self.generate_step_1(story_idea)
    
    def expand_to_paragraph(self, sentence_summary: str, story_idea: str) -> str:
        """Legacy: Generate Step 2: Paragraph expansion."""
        return self.generate_step_2(sentence_summary, story_idea)
    
    def extract_characters(self, story_context: str) -> str:
        """Legacy: Generate Step 3: Character extraction."""
        # Parse story context to extract components
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        return self.generate_step_3(story_idea, sentence_summary, paragraph_summary)
    
    def expand_to_plot(self, story_context: str) -> str:
        """Legacy: Generate Step 4: Plot expansion."""
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        characters = lines[3] if len(lines) > 3 else ""
        return self.generate_step_4(story_idea, sentence_summary, paragraph_summary, characters)
    
    def generate_character_synopses(self, story_context: str) -> str:
        """Legacy: Generate Step 5: Character synopses."""
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        characters = lines[3] if len(lines) > 3 else ""
        detailed_plot = lines[4] if len(lines) > 4 else ""
        return self.generate_step_5(story_idea, sentence_summary, paragraph_summary, characters, detailed_plot)
    
    def expand_to_detailed_plot(self, story_context: str) -> str:
        """Legacy: Generate Step 6: Detailed plot."""
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        characters = lines[3] if len(lines) > 3 else ""
        detailed_plot = lines[4] if len(lines) > 4 else ""
        character_synopses = lines[5] if len(lines) > 5 else ""
        return self.generate_step_6(story_idea, sentence_summary, paragraph_summary, characters, detailed_plot, character_synopses)
    
    def generate_detailed_character_chart(self, story_idea: str, characters: str, character_synopses: str, detailed_plot: str) -> str:
        """Legacy: Generate Step 7: Character charts."""
        return self.generate_step_7(story_idea, characters, character_synopses, detailed_plot)
    
    def generate_scene_breakdown(self, story_context: str) -> str:
        """Legacy: Generate Step 8: Scene breakdown."""
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        characters = lines[3] if len(lines) > 3 else ""
        character_synopses = lines[4] if len(lines) > 4 else ""
        detailed_plot = lines[5] if len(lines) > 5 else ""
        character_charts = lines[6] if len(lines) > 6 else ""
        return self.generate_step_8(story_idea, sentence_summary, paragraph_summary, characters, character_synopses, detailed_plot, character_charts)
    
    def expand_scene(self, story_context: str, scene_info: str) -> str:
        """Legacy: Generate Step 9: Scene expansion."""
        lines = story_context.strip().split('\n')
        story_idea = lines[0] if len(lines) > 0 else ""
        sentence_summary = lines[1] if len(lines) > 1 else ""
        paragraph_summary = lines[2] if len(lines) > 2 else ""
        characters = lines[3] if len(lines) > 3 else ""
        character_synopses = lines[4] if len(lines) > 4 else ""
        detailed_plot = lines[5] if len(lines) > 5 else ""
        character_charts = lines[6] if len(lines) > 6 else ""
        scene_breakdown = lines[7] if len(lines) > 7 else ""
        return self.generate_step_9(story_idea, sentence_summary, paragraph_summary, characters, character_synopses, detailed_plot, character_charts, scene_breakdown)
    
    def generate_chapter_prose(self, story_context: str, scene_expansion: str, chapter_number: int, previous_chapters: str = "", style_instructions: str = "") -> str:
        """Legacy: Generate Step 10: Chapter prose."""
        return self.writer_agent.generate_chapter_prose(story_context, scene_expansion, chapter_number, previous_chapters, style_instructions)
    
    def refine_chapter_prose(self, chapter_content: str, refinement_instructions: str, story_context: str, scene_expansion: str, style_instructions: str = "") -> str:
        """Legacy: Refine chapter prose."""
        return self.writer_agent.refine_chapter_prose(chapter_content, refinement_instructions, story_context, scene_expansion, style_instructions)
    
    def analyze_story(self, story_context: str) -> str:
        """Legacy: Analyze story."""
        return self.analyzer_agent.analyze_story(story_context)
    
    def generate_step_2(self, sentence_summary: str, story_idea: str) -> str:
        """Generate Step 2: Paragraph expansion."""
        return self.paragraph_agent.generate(sentence_summary, story_idea)
    
    def generate_step_3(self, story_idea: str, sentence_summary: str, paragraph_summary: str) -> str:
        """Generate Step 3: Character extraction."""
        characters = self.character_agent.generate(story_idea, sentence_summary, paragraph_summary)
        return json.dumps(characters, indent=2)
    
    def generate_step_4(self, story_idea: str, sentence_summary: str, paragraph_summary: str, characters: str) -> str:
        """Generate Step 4: Plot expansion."""
        return self.plot_agent.generate(story_idea, sentence_summary, paragraph_summary, characters)
    
    def generate_step_5(self, story_idea: str, sentence_summary: str, paragraph_summary: str, characters: str, detailed_plot: str) -> str:
        """Generate Step 5: Character synopses."""
        synopses = self.synopses_agent.generate(story_idea, sentence_summary, paragraph_summary, characters, detailed_plot)
        return json.dumps(synopses, indent=2)
    
    def generate_step_6(self, story_idea: str, sentence_summary: str, paragraph_summary: str, characters: str, detailed_plot: str, character_synopses: str) -> str:
        """Generate Step 6: Detailed plot."""
        return self.detailed_plot_agent.generate(story_idea, sentence_summary, paragraph_summary, characters, detailed_plot, character_synopses)
    
    def generate_step_7(self, story_idea: str, characters: str, character_synopses: str, detailed_plot: str) -> str:
        """Generate Step 7: Character charts."""
        return self.charts_agent.generate(story_idea, characters, character_synopses, detailed_plot)
    
    def generate_step_8(self, story_idea: str, sentence_summary: str, paragraph_summary: str, characters: str, character_synopses: str, detailed_plot: str, character_charts: str) -> str:
        """Generate Step 8: Scene breakdown."""
        scenes = self.breakdown_agent.generate(story_idea, sentence_summary, paragraph_summary, characters, character_synopses, detailed_plot, character_charts)
        return json.dumps(scenes, indent=2)
    
    def generate_step_9(self, story_idea: str, sentence_summary: str, paragraph_summary: str, characters: str, character_synopses: str, detailed_plot: str, character_charts: str, scene_breakdown: str) -> str:
        """Generate Step 9: Scene expansion."""
        scenes = self.expansion_agent.generate(story_idea, sentence_summary, paragraph_summary, characters, character_synopses, detailed_plot, character_charts, scene_breakdown)
        return json.dumps(scenes, indent=2)
    
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