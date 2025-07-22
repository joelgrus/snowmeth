"""AI agents and DSPy signatures for the Snowflake Method."""

import random
import dspy
import dspy.streaming
import json
import logging
from typing import List, Union, Dict, Any, AsyncGenerator
from pydantic import BaseModel, Field, validator
from .config import LLMConfig
from .exceptions import ModelError

logger = logging.getLogger(__name__)


def clean_json_markdown(content: str) -> str:
    """Clean up potential markdown formatting from JSON content."""
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]  # Remove ```json
    if content.endswith("```"):
        content = content[:-3]  # Remove ```
    return content.strip()


class CharacterSummaries(BaseModel):
    """Structured character summaries model"""

    characters: Dict[str, str] = Field(
        description="Dictionary with character names as keys and detailed character summaries as values"
    )


class CharacterSynopses(BaseModel):
    """Structured character synopses model"""

    character_synopses: Dict[str, str] = Field(
        description="Dictionary with character names as keys and character synopses as values"
    )


class SceneExpansion(BaseModel):
    """Structured scene expansion model"""

    scene_number: int = Field(description="Scene number")
    title: str = Field(description="Compelling, specific scene title")
    pov_character: str = Field(description="Point of view character name")
    setting: str = Field(
        description="Detailed description of where and when - include sensory details, time of day, weather, atmosphere"
    )
    scene_goal: str = Field(
        description="Specific story function this scene serves - what plot/character development happens"
    )
    character_goal: str = Field(
        description="Concrete, specific goal the POV character pursues in this scene"
    )
    character_motivation: str = Field(
        description="Deep emotional/psychological reasons driving the character - connect to their backstory and arc"
    )
    obstacles: List[str] = Field(
        description="List of 2-4 specific, concrete obstacles - people, events, internal conflicts"
    )
    conflict_type: str = Field(
        description="Describe the specific tension - internal struggle, interpersonal conflict, external threat"
    )
    key_beats: List[str] = Field(
        description="List of 4-6 specific story moments with concrete actions, dialogue snippets, or emotional beats"
    )
    emotional_arc: str = Field(
        description="Specific emotional journey from opening feeling to closing feeling with turning points"
    )
    scene_outcome: str = Field(
        description="Concrete changes - what is different at scene end vs beginning"
    )
    subplot_elements: List[str] = Field(
        description="Specific subplot threads advanced - name the subplot and how it progresses"
    )
    character_relationships: Union[str, List[str]] = Field(
        description="Specific relationship changes or developments with named characters"
    )
    foreshadowing: Union[str, List[str]] = Field(
        description="Specific hints, symbols, or setup for future plot points"
    )
    estimated_pages: int = Field(description="Estimated page count for this scene")

    @validator("character_relationships", pre=True)
    def convert_relationships_to_string(cls, v):
        if isinstance(v, list):
            return "; ".join(v)
        return v

    @validator("foreshadowing", pre=True)
    def convert_foreshadowing_to_string(cls, v):
        if isinstance(v, list):
            return "; ".join(v)
        return v


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

    story_context: str = dspy.InputField(
        desc="Full story context including sentence and paragraph summaries"
    )
    characters: CharacterSummaries = dspy.OutputField(
        desc="Character summaries with names as keys and detailed summaries as values. Each summary should be 250-300 words covering: character's story goal, motivation, internal/external conflict, character arc, relevant backstory, personality traits, flaws, and how they relate to the main plot. REQUIRED: You must include exactly 4 characters minimum - the protagonist, the main antagonist, and at least 2 key supporting characters who play important roles in the story. Use appropriate character names that fit the story's setting and genre."
    )


class PlotExpander(dspy.Signature):
    """Expand the paragraph summary into a detailed one-page plot summary"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, and character summaries"
    )
    plot_summary = dspy.OutputField(
        desc="A detailed one-page plot summary (400-500 words) that expands the paragraph into a complete plot structure. Develop the story's progression from beginning to end, showing key plot points and how character arcs integrate with the story. Maintain consistency with established characters and their motivations. Use whatever story structure works best for this particular narrative."
    )


class CharacterSynopsisGenerator(dspy.Signature):
    """Generate character synopses telling the story from each character's point of view"""

    story_context: str = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, and plot summary"
    )
    synopses: CharacterSynopses = dspy.OutputField(
        desc="Character synopses with names as keys and synopses as values. Each synopsis should be a one-page description (250-300 words) telling the story from that character's perspective and point of view. Focus on their personal journey, what they experience, their thoughts and feelings, their goals and obstacles, and how they see the other characters and events. Write in a narrative style that captures their voice and perspective."
    )


class DetailedPlotExpander(dspy.Signature):
    """Expand the one-page plot summary into a detailed four-page plot synopsis"""

    story_context = dspy.InputField(
        desc="Full story context including sentence, paragraph, character summaries, plot summary, and character synopses"
    )
    detailed_plot_synopsis = dspy.OutputField(
        desc="Create a comprehensive FOUR-PAGE plot synopsis (1200-1600 words minimum) that significantly expands the existing plot summary. This should be substantially longer and more detailed than the previous step. Break the story into clear acts/sections and include: 1) Detailed opening scenes with rich character establishment and world-building, 2) Complex rising action with multiple plot developments, character interactions, and escalating conflicts, 3) Comprehensive mid-story developments including subplots, character arcs, and relationship dynamics, 4) Detailed climactic sequences with specific action beats and emotional moments, 5) Full resolution covering all plot threads and character conclusions. Include specific dialogue examples, vivid scene descriptions, character emotional states, world-building details, and smooth narrative transitions. Write as flowing prose that reads like a detailed story treatment, not bullet points. Aim for novel-length story complexity with rich narrative depth that could serve as a comprehensive blueprint for writing the full novel."
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
        desc="Create a comprehensive character chart that fully develops this character with rich, specific details. Provide: detailed physical appearance (height, build, distinctive features, scars, clothing, etc.), concrete personality traits and specific mannerisms, complete background story with key life events, clear motivations and goals, defined relationships with other characters, specific skills and abilities, detailed character arc showing how they change, particular fears and strengths, unique speech patterns or catchphrases, and meaningful possessions or symbols. Be creative and specific - invent concrete details that bring this character to life rather than describing what isn't known. Write as flowing, detailed prose that reads like a character bible entry. Use plain text without any markdown formatting - no asterisks, headers, or special symbols."
    )


class SceneBreakdown(BaseModel):
    """Individual scene in a novel breakdown"""

    scene_number: int = Field(description="Scene number in sequence")
    pov_character: str = Field(description="Point of view character for this scene")
    scene_description: str = Field(
        description="2-3 sentences describing major events and character development"
    )
    estimated_pages: int = Field(
        description="Estimated page count - should be substantial (20-50 pages) for chapter-length scenes"
    )


class NovelSceneBreakdown(BaseModel):
    """Complete scene breakdown for a novel"""

    scenes: List[SceneBreakdown] = Field(description="List of all scenes in the novel")
    total_estimated_pages: int = Field(
        description="Total estimated pages for the complete novel"
    )


class SceneBreakdownGenerator(dspy.Signature):
    """Break down the four-page plot synopsis into individual chapter-length scenes for a novel"""

    story_context: str = dspy.InputField(
        desc="Full story context including all previous steps, especially the detailed four-page plot synopsis from Step 6"
    )
    scene_breakdown: NovelSceneBreakdown = dspy.OutputField(
        desc="Break down the plot synopsis into substantial chapter-length scenes. Each scene should be a major story section. The number of scenes should be determined by the story's natural structure, but should be at least 20. Scenes should typically be 10-20 pages each to create a full novel (200-500 pages total)."
    )


# Story Analysis Models
class POVAnalysis(BaseModel):
    """POV distribution and issues analysis"""

    distribution: Dict[str, int] = Field(
        description="Character name to scene count mapping"
    )
    issues: List[str] = Field(description="List of POV-related problems")
    recommendations: List[str] = Field(description="Suggestions for POV improvements")


class CharacterAnalysis(BaseModel):
    """Character development and consistency analysis"""

    main_characters: List[str] = Field(description="List of main character names")
    forgotten_characters: List[str] = Field(
        description="Characters mentioned early but absent from later scenes"
    )
    character_arc_issues: List[str] = Field(
        description="Characters whose arcs seem incomplete or inconsistent"
    )
    relationship_tracking: List[str] = Field(
        description="Missing or inconsistent character relationships"
    )


class SubplotAnalysis(BaseModel):
    """Subplot tracking and resolution analysis"""

    identified_subplots: List[str] = Field(description="List of subplot threads found")
    incomplete_subplots: List[str] = Field(
        description="Subplots that are introduced but not resolved"
    )
    missing_connections: List[str] = Field(
        description="Subplots that should connect but don't"
    )
    resolution_issues: List[str] = Field(
        description="Subplots with unclear or missing resolutions"
    )


class StoryStructure(BaseModel):
    """Overall story structure and pacing analysis"""

    pacing_issues: List[str] = Field(description="Scenes that feel rushed or too slow")
    plot_holes: List[str] = Field(
        description="Logical inconsistencies or missing explanations"
    )
    foreshadowing_analysis: List[str] = Field(
        description="Foreshadowing elements that need payoff"
    )
    climax_buildup: List[str] = Field(
        description="Issues with tension building toward climax"
    )


class ConsistencyChecks(BaseModel):
    """Consistency verification across the story"""

    timeline_issues: List[str] = Field(
        description="Chronological problems or contradictions"
    )
    setting_consistency: List[str] = Field(
        description="Location or world-building inconsistencies"
    )
    character_voice: List[str] = Field(description="Characters acting out of character")
    tone_shifts: List[str] = Field(description="Unexpected or jarring tone changes")


class CompletenessAnalysis(BaseModel):
    """Story completeness and resolution tracking"""

    unresolved_threads: List[str] = Field(
        description="Story elements introduced but not concluded"
    )
    missing_scenes: List[str] = Field(description="Gaps in the story that need scenes")
    character_motivations: List[str] = Field(
        description="Unclear or inconsistent character motivations"
    )
    thematic_coherence: List[str] = Field(
        description="Whether themes are consistently developed"
    )


class SceneImprovement(BaseModel):
    """Individual scene improvement recommendation"""

    scene_number: int = Field(description="Scene number to improve")
    priority: str = Field(description="Priority level: high, medium, low")
    issue: str = Field(description="Description of the issue")
    suggestion: str = Field(description="Specific improvement suggestion")


class StoryRecommendations(BaseModel):
    """Prioritized improvement recommendations"""

    high_priority: List[str] = Field(
        description="Critical issues that must be addressed"
    )
    medium_priority: List[str] = Field(description="Important improvements to consider")
    low_priority: List[str] = Field(description="Minor polish suggestions")
    scene_improvements: List[SceneImprovement] = Field(
        description="Scene-specific improvement suggestions"
    )


class OverallAssessment(BaseModel):
    """Overall story quality assessment"""

    strengths: List[str] = Field(description="What works well in the story")
    weaknesses: List[str] = Field(description="Areas that need improvement")
    readiness_score: str = Field(description="Score out of 10 (e.g., '7/10')")
    key_strengths: List[str] = Field(description="Top 3-5 strengths")
    improvement_areas: List[str] = Field(description="Top 3-5 areas for improvement")


class StoryAnalysis(BaseModel):
    """Complete story analysis model"""

    pov_analysis: POVAnalysis = Field(description="Point of view analysis")
    character_analysis: CharacterAnalysis = Field(
        description="Character development analysis"
    )
    subplot_analysis: SubplotAnalysis = Field(description="Subplot tracking analysis")
    story_structure: StoryStructure = Field(description="Story structure analysis")
    consistency_checks: ConsistencyChecks = Field(
        description="Consistency verification"
    )
    completeness_analysis: CompletenessAnalysis = Field(
        description="Story completeness analysis"
    )
    recommendations: StoryRecommendations = Field(
        description="Improvement recommendations"
    )
    overall_assessment: OverallAssessment = Field(
        description="Overall quality assessment"
    )


class DetailedSceneExpansion(BaseModel):
    """Detailed scene expansion model for Step 9"""

    scene_number: int = Field(description="Scene number")
    title: str = Field(description="Compelling, specific scene title")
    pov_character: str = Field(description="Point of view character name")
    setting: str = Field(
        description="Detailed description of where and when - include sensory details, time of day, weather, atmosphere"
    )
    scene_goal: str = Field(
        description="Specific story function this scene serves - what plot/character development happens"
    )
    character_goal: str = Field(
        description="Concrete, specific goal the POV character pursues in this scene"
    )
    character_motivation: str = Field(
        description="Deep emotional/psychological reasons driving the character - connect to their backstory and arc"
    )
    obstacles: List[str] = Field(
        description="List 2-4 specific, concrete obstacles - people, events, internal conflicts"
    )
    conflict_type: str = Field(
        description="Describe the specific tension - internal struggle, interpersonal conflict, external threat"
    )
    key_beats: List[str] = Field(
        description="List 4-6 specific story moments with concrete actions, dialogue snippets, or emotional beats"
    )
    emotional_arc: str = Field(
        description="Specific emotional journey from opening feeling to closing feeling with turning points"
    )
    scene_outcome: str = Field(
        description="Concrete changes - what is different at scene end vs beginning"
    )
    subplot_elements: List[str] = Field(
        description="Specific subplot threads advanced - name the subplot and how it progresses"
    )
    character_relationships: str = Field(
        description="Specific relationship changes or developments with named characters"
    )
    foreshadowing: str = Field(
        description="Specific hints, symbols, or setup for future plot points"
    )
    estimated_pages: int = Field(description="Estimated page count for this scene")


class StoryAnalyzer(dspy.Signature):
    """Analyze the complete story for consistency, POV distribution, subplot tracking, and narrative completeness"""

    story_context: str = dspy.InputField(
        desc="Complete story context including all steps 1-9, especially detailed scene expansions from Step 9"
    )
    analysis_report: StoryAnalysis = dspy.OutputField(
        desc="Provide a comprehensive analysis of the story covering POV distribution, character development, subplot tracking, story structure, consistency checks, completeness analysis, and prioritized recommendations for improvement."
    )


class SceneExpansionGenerator(dspy.Signature):
    """Expand individual scenes into detailed, specific mini-outlines with concrete character goals, conflicts, and story beats"""

    story_context: str = dspy.InputField(
        desc="Full story context including all previous steps, character information, and plot details"
    )
    scene_info: str = dspy.InputField(
        desc="Information about the specific scene to expand, including scene number, POV character, description, and estimated pages"
    )
    scene_expansion: DetailedSceneExpansion = dspy.OutputField(
        desc="Create a detailed, specific scene expansion. Be concrete and specific, not generic. Include actual dialogue snippets, specific actions, and vivid details. Write as if creating a detailed scene outline for a professional novelist."
    )


class SceneImprover(dspy.Signature):
    """Improve a specific scene based on targeted feedback and analysis issues"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps, character information, and plot details"
    )
    scene_info = dspy.InputField(
        desc="Information about the specific scene to improve, including scene number, POV character, description, and estimated pages"
    )
    current_expansion = dspy.InputField(
        desc="Current scene expansion that needs improvement"
    )
    improvement_guidance = dspy.InputField(
        desc="Specific issues to address and improvements to make based on story analysis"
    )
    improved_scene: DetailedSceneExpansion = dspy.OutputField(
        desc="Improve the scene expansion based on the guidance provided. CRITICAL RULES: 1) DO NOT change the title unless the improvement_guidance specifically mentions title issues or the current title is clearly a placeholder (contains 'Placeholder' or 'Scene N'). Keep existing titles unless there is a compelling story reason to change them. 2) Focus improvements on content: character_motivation, key_beats, emotional_arc, scene_goal, obstacles, and other story elements. 3) Address the specific issues in improvement_guidance through content improvements, not title changes."
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
            self.scene_expansion_generator = dspy.ChainOfThought(
                SceneExpansionGenerator
            )
            self.story_analyzer = dspy.ChainOfThought(StoryAnalyzer)
            self.scene_improver = dspy.ChainOfThought(SceneImprover)
        except Exception as e:
            raise ModelError(
                f"Failed to initialize AI model '{default_model}'. Check your API key and internet connection. Error: {e}"
            )

    def generate_sentence(self, story_idea: str) -> str:
        """Generate initial one-sentence summary"""
        # Add randomness to avoid caching
        unique_prompt = f"{story_idea} [seed: {random.randint(1000, 9999)}]"
        result = self.generator(story_idea=unique_prompt)
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
        # Add randomness to avoid caching
        unique_idea = f"{story_idea} [seed: {random.randint(1000, 9999)}]"

        result = self.expander(sentence_summary=sentence, story_idea=unique_idea)

        return result.paragraph_summary

    def extract_characters(self, story_context: str) -> str:
        """Extract main characters and create character summaries"""
        import json

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.character_extractor(story_context=unique_context)

        # The structured output should give us a CharacterSummaries object
        # result.characters is the CharacterSummaries model instance
        # result.characters.characters is the dict we want
        character_dict = result.characters.characters

        # Ensure we return valid JSON
        return json.dumps(character_dict, ensure_ascii=False, indent=2)

    def expand_to_plot(self, story_context: str) -> str:
        """Expand story context into detailed one-page plot summary"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.plot_expander(story_context=unique_context)
        return result.plot_summary

    def generate_character_synopses(self, story_context: str) -> str:
        """Generate character synopses from each character's POV"""
        import json

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.character_synopsis_generator(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        character_synopses = result.synopses.character_synopses

        # Filter out entries with empty values
        filtered_synopses = {
            name: synopsis
            for name, synopsis in character_synopses.items()
            if synopsis and synopsis.strip()
        }

        return json.dumps(filtered_synopses, ensure_ascii=False, indent=2)

    def expand_to_detailed_plot(self, story_context: str) -> str:
        """Expand to detailed four-page plot synopsis for Step 6"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.detailed_plot_expander(story_context=unique_context)
        return result.detailed_plot_synopsis

    def generate_detailed_character_chart(
        self, story_context: str, character_name: str
    ) -> str:
        """Generate detailed character chart for a single character for Step 7"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.detailed_character_chart_generator(
            story_context=unique_context,
            character_name=character_name,
        )
        return result.character_chart

    def generate_scene_breakdown(self, story_context: str) -> str:
        """Generate scene breakdown from four-page plot synopsis for Step 8"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_breakdown_generator(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        scenes_list = [scene.dict() for scene in result.scene_breakdown.scenes]
        return json.dumps(scenes_list, indent=2)

    def expand_scene(self, story_context: str, scene_info: str) -> str:
        """Expand a single scene into detailed mini-outline for Step 9"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_expansion_generator(
            story_context=unique_context, scene_info=scene_info
        )

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.scene_expansion.dict(), indent=2)

    def improve_scene(
        self,
        story_context: str,
        scene_info: str,
        current_expansion: str,
        improvement_guidance: str,
    ) -> str:
        """Improve a specific scene with targeted feedback"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_improver(
            story_context=unique_context,
            scene_info=scene_info,
            current_expansion=current_expansion,
            improvement_guidance=improvement_guidance,
        )

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.improved_scene.dict(), indent=2)

    def analyze_story(self, story_context: str) -> str:
        """Analyze complete story for consistency and completeness for Step 9.5"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.story_analyzer(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.analysis_report.dict(), indent=2)

    def generate_chapter_prose(
        self,
        story_context: str,
        scene_data: Dict[str, Any],
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        writing_style: str = "",
        previous_chapter_content: str = None,
    ) -> str:
        """Generate full chapter prose based on scene expansion data"""

        class ChapterWriter(dspy.Signature):
            """Write a complete novel chapter based on the provided scene expansion and context.

            CRITICAL REQUIREMENTS:
            - Write a VERY LONG chapter (15,000-25,000 words minimum)
            - This should be a substantial portion of a novel, not a short story
            - Include extensive dialogue, action, description, and character development
            - Follow the scene expansion details closely
            - Maintain consistency with previous chapters
            - NO MARKDOWN HEADERS - start directly with the prose, no "Chapter X" titles
            - Show rather than tell through scenes and dialogue
            - Have a clear beginning, middle, and end within this chapter
            - Advance the overall story arc significantly
            - Use engaging, literary prose appropriate for a full-length novel
            - Focus on the POV character's experience and emotions
            - Build tension and conflict as outlined in the scene expansion
            - Include rich sensory details and atmosphere
            - Develop character relationships through dialogue and action
            - Create compelling scenes that could stand alone but advance the plot
            - MATCH THE WRITING STYLE of the previous chapter (if provided) - mimic tone, voice, pacing, dialogue style

            LENGTH IS CRITICAL: This must be novel-chapter length, not a summary or outline.
            Write the full prose with complete scenes, not abbreviated or shortened content.

            STYLE CONSISTENCY: If a previous chapter is provided, carefully study its writing style,
            voice, dialogue patterns, descriptive approach, and narrative tone. Match these elements
            closely to maintain consistency throughout the novel.
            """

            story_context = dspy.InputField(
                desc="Complete story context including all previous steps"
            )
            scene_expansion = dspy.InputField(
                desc="Detailed scene expansion with goals, obstacles, beats, etc."
            )
            chapter_number = dspy.InputField(desc="The chapter number being written")
            previous_chapters = dspy.InputField(
                desc="Summary of previous chapters for continuity"
            )
            writing_style = dspy.InputField(
                desc="Specific writing style instructions to follow"
            )
            previous_chapter_sample = dspy.InputField(
                desc="Full content of the previous chapter to match writing style (if available)"
            )
            chapter_prose = dspy.OutputField(
                desc="Complete novel chapter prose (15,000-25,000 words minimum, NO markdown headers)"
            )

        # Create a ChapterWriter chain
        chapter_writer = dspy.ChainOfThought(ChapterWriter)

        # Prepare previous chapters context
        prev_chapters_text = ""
        if previous_chapters:
            prev_chapters_text = "\n\nPrevious Chapters:\n"
            for ch in previous_chapters:
                prev_chapters_text += (
                    f"Chapter {ch['chapter_number']}: {ch['summary']}\n"
                )

        # Prepare scene expansion details
        scene_text = f"Chapter {chapter_number}: {scene_data.get('title', '')}\n\n"
        scene_text += f"POV Character: {scene_data.get('pov_character', '')}\n"
        scene_text += f"Setting: {scene_data.get('setting', '')}\n"
        scene_text += f"Scene Goal: {scene_data.get('scene_goal', '')}\n"
        scene_text += f"Character Goal: {scene_data.get('character_goal', '')}\n"
        scene_text += (
            f"Character Motivation: {scene_data.get('character_motivation', '')}\n"
        )

        if scene_data.get("obstacles"):
            scene_text += "Obstacles:\n"
            for obstacle in scene_data["obstacles"]:
                scene_text += f"- {obstacle}\n"

        scene_text += f"Conflict Type: {scene_data.get('conflict_type', '')}\n"

        if scene_data.get("key_beats"):
            scene_text += "\nKey Story Beats:\n"
            for beat in scene_data["key_beats"]:
                scene_text += f"- {beat}\n"

        scene_text += f"\nEmotional Arc: {scene_data.get('emotional_arc', '')}\n"
        scene_text += f"Scene Outcome: {scene_data.get('scene_outcome', '')}\n"

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Prepare writing style instructions
        style_instructions = (
            writing_style.strip()
            if writing_style
            else "Write in clear, engaging prose suitable for a novel."
        )

        # Prepare previous chapter content for style matching
        prev_chapter_sample = ""
        if previous_chapter_content:
            # Limit to first 2000 characters to avoid token limits while providing style sample
            prev_chapter_sample = (
                previous_chapter_content[:2000] + "..."
                if len(previous_chapter_content) > 2000
                else previous_chapter_content
            )
        else:
            prev_chapter_sample = (
                "No previous chapter available - this is the first chapter."
            )

        # Generate the chapter
        result = chapter_writer(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            previous_chapters=prev_chapters_text,
            writing_style=style_instructions,
            previous_chapter_sample=prev_chapter_sample,
        )

        return result.chapter_prose

    def refine_chapter_prose(
        self,
        story_context: str,
        chapter_number: int,
        current_content: str,
        scene_data: Dict[str, Any],
        instructions: str,
    ) -> str:
        """Refine an existing chapter with specific instructions"""

        class ChapterRefiner(dspy.Signature):
            """Refine an existing novel chapter based on specific instructions.

            CRITICAL REQUIREMENTS:
            - Keep the chapter VERY LONG (15,000-25,000 words minimum) - do not shorten it
            - Apply the specific refinement instructions while maintaining the chapter's structure
            - Preserve the overall plot progression and character development
            - Maintain consistency with the scene expansion requirements
            - NO MARKDOWN HEADERS - keep the same format as the original
            - Keep the same writing style and voice as the original chapter
            - Make targeted improvements without losing the chapter's essence

            REFINEMENT APPROACH:
            - Read the current chapter content carefully
            - Identify what the refinement instructions are asking for
            - Make specific improvements while keeping everything else intact
            - Ensure the refined version is still complete and substantial
            - Do not summarize or shorten - maintain full novel-chapter length
            """

            story_context = dspy.InputField(
                desc="Complete story context including all previous steps"
            )
            scene_expansion = dspy.InputField(
                desc="Scene expansion that this chapter should follow"
            )
            chapter_number = dspy.InputField(desc="The chapter number being refined")
            current_content = dspy.InputField(
                desc="The current chapter content to be refined"
            )
            refinement_instructions = dspy.InputField(
                desc="Specific instructions for how to refine the chapter"
            )
            refined_chapter = dspy.OutputField(
                desc="The refined chapter with improvements applied (15,000-25,000 words, NO markdown headers)"
            )

        # Create a ChapterRefiner chain
        chapter_refiner = dspy.ChainOfThought(ChapterRefiner)

        # Prepare scene expansion details
        scene_text = f"Chapter {chapter_number}: {scene_data.get('title', '')}\n\n"
        scene_text += f"POV Character: {scene_data.get('pov_character', '')}\n"
        scene_text += f"Setting: {scene_data.get('setting', '')}\n"
        scene_text += f"Scene Goal: {scene_data.get('scene_goal', '')}\n"
        scene_text += f"Character Goal: {scene_data.get('character_goal', '')}\n"
        scene_text += (
            f"Character Motivation: {scene_data.get('character_motivation', '')}\n"
        )

        if scene_data.get("obstacles"):
            scene_text += "Obstacles:\n"
            for obstacle in scene_data["obstacles"]:
                scene_text += f"- {obstacle}\n"

        scene_text += f"Conflict Type: {scene_data.get('conflict_type', '')}\n"

        if scene_data.get("key_beats"):
            scene_text += "\nKey Story Beats:\n"
            for beat in scene_data["key_beats"]:
                scene_text += f"- {beat}\n"

        scene_text += f"\nEmotional Arc: {scene_data.get('emotional_arc', '')}\n"
        scene_text += f"Scene Outcome: {scene_data.get('scene_outcome', '')}\n"

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Refine the chapter
        result = chapter_refiner(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            current_content=current_content,
            refinement_instructions=instructions,
        )

        return result.refined_chapter

    async def refine_chapter_prose_stream(
        self,
        story_context: str,
        chapter_number: int,
        current_content: str,
        scene_data: Dict[str, Any],
        instructions: str,
    ) -> AsyncGenerator[str, None]:
        """Refine an existing chapter with specific instructions - streaming version"""

        class ChapterRefiner(dspy.Signature):
            """Refine an existing novel chapter based on specific instructions.

            CRITICAL REQUIREMENTS:
            - Keep the chapter VERY LONG (15,000-25,000 words minimum) - do not shorten it
            - Apply the specific refinement instructions while maintaining the chapter's structure
            - Preserve the overall plot progression and character development
            - Maintain consistency with the scene expansion requirements
            - NO MARKDOWN HEADERS - keep the same format as the original
            - Keep the same writing style and voice as the original chapter
            - Make targeted improvements without losing the chapter's essence

            REFINEMENT APPROACH:
            - Read the current chapter content carefully
            - Identify what the refinement instructions are asking for
            - Make specific improvements while keeping everything else intact
            - Ensure the refined version is still complete and substantial
            - Do not summarize or shorten - maintain full novel-chapter length
            """

            story_context = dspy.InputField(
                desc="Complete story context including all previous steps"
            )
            scene_expansion = dspy.InputField(
                desc="Scene expansion that this chapter should follow"
            )
            chapter_number = dspy.InputField(desc="The chapter number being refined")
            current_content = dspy.InputField(
                desc="The current chapter content to be refined"
            )
            refinement_instructions = dspy.InputField(
                desc="Specific instructions for how to refine the chapter"
            )
            refined_chapter = dspy.OutputField(
                desc="The refined chapter with improvements applied (15,000-25,000 words, NO markdown headers)"
            )

        # Create a ChapterRefiner chain with streaming
        chapter_refiner = dspy.ChainOfThought(ChapterRefiner)

        # Prepare scene expansion details
        scene_text = f"Chapter {chapter_number}: {scene_data.get('title', '')}\n\n"
        scene_text += f"POV Character: {scene_data.get('pov_character', '')}\n"
        scene_text += f"Setting: {scene_data.get('setting', '')}\n"
        scene_text += f"Scene Goal: {scene_data.get('scene_goal', '')}\n"
        scene_text += f"Character Goal: {scene_data.get('character_goal', '')}\n"
        scene_text += (
            f"Character Motivation: {scene_data.get('character_motivation', '')}\n"
        )

        if scene_data.get("obstacles"):
            scene_text += "Obstacles:\n"
            for obstacle in scene_data["obstacles"]:
                scene_text += f"- {obstacle}\n"

        scene_text += f"Conflict Type: {scene_data.get('conflict_type', '')}\n"

        if scene_data.get("key_beats"):
            scene_text += "\nKey Story Beats:\n"
            for beat in scene_data["key_beats"]:
                scene_text += f"- {beat}\n"

        scene_text += f"\nEmotional Arc: {scene_data.get('emotional_arc', '')}\n"
        scene_text += f"Scene Outcome: {scene_data.get('scene_outcome', '')}\n"

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Wrap the chapter refiner with streaming support
        stream_refiner = dspy.streamify(
            chapter_refiner,
            stream_listeners=[
                dspy.streaming.StreamListener(signature_field_name="refined_chapter")
            ],
        )

        # Generate the refined chapter with streaming
        output = stream_refiner(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            current_content=current_content,
            refinement_instructions=instructions,
        )

        async for chunk in output:
            if isinstance(chunk, dspy.streaming.StreamResponse):
                # Extract just the chunk content from the StreamResponse
                yield chunk.chunk

    async def generate_chapter_prose_stream(
        self,
        story_context: str,
        scene_data: Dict[str, Any],
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        writing_style: str = "",
        previous_chapter_content: str = None,
    ) -> AsyncGenerator[str, None]:
        """Generate full chapter prose with streaming support"""

        class ChapterWriter(dspy.Signature):
            """Write a complete novel chapter based on the provided scene expansion and context.

            CRITICAL REQUIREMENTS:
            - Write a VERY LONG chapter (15,000-25,000 words minimum)
            - This should be a substantial portion of a novel, not a short story
            - Include extensive dialogue, action, description, and character development
            - Follow the scene expansion details closely
            - Maintain consistency with previous chapters
            - NO MARKDOWN HEADERS - start directly with the prose, no "Chapter X" titles
            - Show rather than tell through scenes and dialogue
            - Have a clear beginning, middle, and end within this chapter
            - Advance the overall story arc significantly
            - Use engaging, literary prose appropriate for a full-length novel
            - Focus on the POV character's experience and emotions
            - Build tension and conflict as outlined in the scene expansion
            - Include rich sensory details and atmosphere
            - Develop character relationships through dialogue and action
            - Create compelling scenes that could stand alone but advance the plot
            - MATCH THE WRITING STYLE of the previous chapter (if provided) - mimic tone, voice, pacing, dialogue style

            LENGTH IS CRITICAL: This must be novel-chapter length, not a summary or outline.
            Write the full prose with complete scenes, not abbreviated or shortened content.

            STYLE CONSISTENCY: If a previous chapter is provided, carefully study its writing style,
            voice, dialogue patterns, descriptive approach, and narrative tone. Match these elements
            closely to maintain consistency throughout the novel.
            """

            story_context = dspy.InputField(
                desc="Complete story context including all previous steps"
            )
            scene_expansion = dspy.InputField(
                desc="Detailed scene expansion with goals, obstacles, beats, etc."
            )
            chapter_number = dspy.InputField(desc="The chapter number being written")
            previous_chapters = dspy.InputField(
                desc="Summary of previous chapters for continuity"
            )
            writing_style = dspy.InputField(
                desc="Specific writing style instructions to follow"
            )
            previous_chapter_sample = dspy.InputField(
                desc="Full content of the previous chapter to match writing style (if available)"
            )
            chapter_prose = dspy.OutputField(
                desc="Complete novel chapter prose (15,000-25,000 words minimum, NO markdown headers)"
            )

        # Create a ChapterWriter chain with streaming
        chapter_writer = dspy.ChainOfThought(ChapterWriter)

        # Prepare previous chapters context
        prev_chapters_text = ""
        if previous_chapters:
            prev_chapters_text = "\n\nPrevious Chapters:\n"
            for ch in previous_chapters:
                prev_chapters_text += (
                    f"Chapter {ch['chapter_number']}: {ch['summary']}\n"
                )

        # Prepare scene expansion details
        scene_text = f"Chapter {chapter_number}: {scene_data.get('title', '')}\n\n"
        scene_text += f"POV Character: {scene_data.get('pov_character', '')}\n"
        scene_text += f"Setting: {scene_data.get('setting', '')}\n"
        scene_text += f"Scene Goal: {scene_data.get('scene_goal', '')}\n"
        scene_text += f"Character Goal: {scene_data.get('character_goal', '')}\n"
        scene_text += (
            f"Character Motivation: {scene_data.get('character_motivation', '')}\n"
        )

        if scene_data.get("obstacles"):
            scene_text += "Obstacles:\n"
            for obstacle in scene_data["obstacles"]:
                scene_text += f"- {obstacle}\n"

        scene_text += f"Conflict Type: {scene_data.get('conflict_type', '')}\n"

        if scene_data.get("key_beats"):
            scene_text += "\nKey Story Beats:\n"
            for beat in scene_data["key_beats"]:
                scene_text += f"- {beat}\n"

        scene_text += f"\nEmotional Arc: {scene_data.get('emotional_arc', '')}\n"
        scene_text += f"Scene Outcome: {scene_data.get('scene_outcome', '')}\n"

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Prepare writing style instructions
        style_instructions = (
            writing_style.strip()
            if writing_style
            else "Write in clear, engaging prose suitable for a novel."
        )

        # Prepare previous chapter content for style matching
        prev_chapter_sample = ""
        if previous_chapter_content:
            # Limit to first 2000 characters to avoid token limits while providing style sample
            prev_chapter_sample = (
                previous_chapter_content[:2000] + "..."
                if len(previous_chapter_content) > 2000
                else previous_chapter_content
            )
        else:
            prev_chapter_sample = (
                "No previous chapter available - this is the first chapter."
            )

        # Wrap the chapter writer with streaming support
        stream_writer = dspy.streamify(
            chapter_writer,
            stream_listeners=[
                dspy.streaming.StreamListener(signature_field_name="chapter_prose")
            ],
        )

        # Generate the chapter with streaming
        output = stream_writer(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            previous_chapters=prev_chapters_text,
            writing_style=style_instructions,
            previous_chapter_sample=prev_chapter_sample,
        )

        async for chunk in output:
            if isinstance(chunk, dspy.streaming.StreamResponse):
                # Extract just the chunk content from the StreamResponse
                yield chunk.chunk
