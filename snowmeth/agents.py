"""AI agents and DSPy signatures for the Snowflake Method."""

import random
import dspy
import json
from typing import List, Union, Dict
from pydantic import BaseModel, Field, validator
from .config import LLMConfig
from .exceptions import ModelError


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
        desc="A comprehensive four-page plot synopsis that expands the existing plot summary into extensive detail. Write as a flowing narrative that covers the story from beginning to end. Include detailed scene descriptions, character interactions, specific plot developments, emotional beats, world-building details, and smooth transitions between events. Maintain consistency with established characters and their motivations while adding rich narrative depth. Write in paragraph form that follows the natural flow of this particular story."
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
        desc="A comprehensive character chart containing relevant details about this character: name and any aliases, physical description, personality traits and quirks, background and personal history, relationships, skills and abilities, goals and motivations, internal and external conflicts, character arc, fears and vulnerabilities, strengths, speech patterns and mannerisms, important possessions or symbols, and role in the story. Include the details that matter most for this particular character and story. Write in detailed prose form, not as a list or bullet points."
    )


class SceneBreakdownGenerator(dspy.Signature):
    """Break down the four-page plot synopsis into individual scenes for a novel"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps, especially the detailed four-page plot synopsis from Step 6"
    )
    scene_breakdown = dspy.OutputField(
        desc='JSON array of scene objects breaking down the four-page plot synopsis into individual scenes. Each scene should be an object with: "scene_number" (integer), "pov_character" (string - which character\'s point of view), "scene_description" (string - 2-3 sentences describing what happens in this scene), "estimated_pages" (integer - rough estimate of pages this scene might take, typically 8-20 pages for major scenes, 4-12 pages for smaller scenes). Aim for 15-25 scenes total to cover the full novel, targeting 250-400 total pages. Focus on key dramatic moments, character interactions, plot advancement, and emotional beats. Format: [{"scene_number": 1, "pov_character": "Character Name", "scene_description": "Description of what happens...", "estimated_pages": 12}, ...]'
    )


class StoryAnalyzer(dspy.Signature):
    """Analyze the complete story for consistency, POV distribution, subplot tracking, and narrative completeness"""

    story_context = dspy.InputField(
        desc="Complete story context including all steps 1-9, especially detailed scene expansions from Step 9"
    )
    analysis_report = dspy.OutputField(
        desc='JSON object containing comprehensive story analysis with the following structure: {"pov_analysis": {"distribution": {"Character Name": scene_count}, "issues": ["List of POV-related problems"], "recommendations": ["Suggestions for POV improvements"]}, "character_analysis": {"main_characters": ["List of main character names"], "forgotten_characters": ["Characters mentioned early but absent from later scenes"], "character_arc_issues": ["Characters whose arcs seem incomplete or inconsistent"], "relationship_tracking": ["Missing or inconsistent character relationships"]}, "subplot_analysis": {"identified_subplots": ["List of subplot threads found"], "incomplete_subplots": ["Subplots that are introduced but not resolved"], "missing_connections": ["Subplots that should connect but don\'t"], "resolution_issues": ["Subplots with unclear or missing resolutions"]}, "story_structure": {"pacing_issues": ["Scenes that feel rushed or too slow"], "plot_holes": ["Logical inconsistencies or missing explanations"], "foreshadowing_analysis": ["Foreshadowing elements that need payoff"], "climax_buildup": ["Issues with tension building toward climax"]}, "consistency_checks": {"timeline_issues": ["Chronological problems or contradictions"], "setting_consistency": ["Location or world-building inconsistencies"], "character_voice": ["Characters acting out of character"], "tone_shifts": ["Unexpected or jarring tone changes"]}, "completeness_analysis": {"unresolved_threads": ["Story elements introduced but not concluded"], "missing_scenes": ["Gaps in the story that need scenes"], "character_motivations": ["Unclear or inconsistent character motivations"], "thematic_coherence": ["Whether themes are consistently developed"]}, "recommendations": {"high_priority": ["Critical issues that must be addressed"], "medium_priority": ["Important improvements to consider"], "low_priority": ["Minor polish suggestions"], "scene_improvements": [{"scene_number": 1, "priority": "high", "issue": "Description of the issue", "suggestion": "Specific improvement suggestion"}]}, "overall_assessment": {"strengths": ["What works well in the story"], "weaknesses": ["Areas that need improvement"], "readiness_score": "X/10", "key_strengths": ["Top 3-5 strengths"], "improvement_areas": ["Top 3-5 areas for improvement"]}}'
    )


class SceneExpansionGenerator(dspy.Signature):
    """Expand individual scenes into detailed, specific mini-outlines with concrete character goals, conflicts, and story beats"""

    story_context = dspy.InputField(
        desc="Full story context including all previous steps, character information, and plot details"
    )
    scene_info = dspy.InputField(
        desc="Information about the specific scene to expand, including scene number, POV character, description, and estimated pages"
    )
    scene_expansion = dspy.OutputField(
        desc='JSON object containing a detailed, specific scene expansion. IMPORTANT: Be concrete and specific, not generic. Include actual dialogue snippets, specific actions, and vivid details. Structure: {"scene_number": integer, "title": "Compelling, specific scene title", "pov_character": "Character name", "setting": "Detailed description of where and when - include sensory details, time of day, weather, atmosphere", "scene_goal": "Specific story function this scene serves - what plot/character development happens", "character_goal": "Concrete, specific goal the POV character pursues in this scene", "character_motivation": "Deep emotional/psychological reasons driving the character - connect to their backstory and arc", "obstacles": ["List 2-4 specific, concrete obstacles - people, events, internal conflicts"], "conflict_type": "Describe the specific tension - internal struggle, interpersonal conflict, external threat", "key_beats": ["List 4-6 specific story moments with concrete actions, dialogue snippets, or emotional beats"], "emotional_arc": "Specific emotional journey from opening feeling to closing feeling with turning points", "scene_outcome": "Concrete changes - what is different at scene end vs beginning", "subplot_elements": ["Specific subplot threads advanced - name the subplot and how it progresses"], "character_relationships": "Specific relationship changes or developments with named characters", "foreshadowing": "Specific hints, symbols, or setup for future plot points", "estimated_pages": integer}. Write as if creating a detailed scene outline for a professional novelist.'
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
    improved_scene = dspy.OutputField(
        desc='Valid JSON object with double quotes containing the improved scene expansion. CRITICAL RULES: 1) DO NOT change the title unless the improvement_guidance specifically mentions title issues or the current title is clearly a placeholder (contains "Placeholder" or "Scene N"). Keep existing titles unless there is a compelling story reason to change them. 2) Focus improvements on content: character_motivation, key_beats, emotional_arc, scene_goal, obstacles, and other story elements. 3) Use proper JSON format with double quotes. 4) Address the specific issues in improvement_guidance through content improvements, not title changes. Return ONLY valid JSON: {"scene_number": integer, "title": "KEEP EXISTING TITLE unless specifically problematic", "pov_character": "Character name", "setting": "Enhanced setting with sensory details", "scene_goal": "Improved story function and plot advancement", "character_goal": "Enhanced concrete goal", "character_motivation": "Deeper psychological drivers with backstory connections", "obstacles": ["Enhanced 2-4 specific obstacles"], "conflict_type": "Refined tension description", "key_beats": ["Enhanced 4-6 story moments with specific actions/dialogue"], "emotional_arc": "Improved emotional journey with clear turning points", "scene_outcome": "Enhanced concrete changes and consequences", "subplot_elements": ["Improved subplot progressions"], "character_relationships": "Enhanced relationship developments", "foreshadowing": "Improved future plot setup", "estimated_pages": integer}'
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
        if hasattr(result, "characters") and hasattr(result.characters, "characters"):
            return json.dumps(result.characters.characters, ensure_ascii=False)

        # Fallback to old behavior if structured output fails
        return json.dumps({}, ensure_ascii=False)

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

        # The structured output should give us a CharacterSynopses object
        if hasattr(result, "synopses") and hasattr(
            result.synopses, "character_synopses"
        ):
            return json.dumps(result.synopses.character_synopses, ensure_ascii=False)

        # Fallback to empty dict if structured output fails
        return json.dumps({}, ensure_ascii=False)

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
        return result.scene_breakdown

    def expand_scene(self, story_context: str, scene_info: str) -> str:
        """Expand a single scene into detailed mini-outline for Step 9"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.scene_expansion_generator(
            story_context=unique_context, scene_info=scene_info
        )

        # Clean up potential markdown formatting
        content = result.scene_expansion.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        return content

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

        # Clean up potential markdown formatting
        content = result.improved_scene.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        # Validate JSON
        try:
            json.loads(content)
            return content
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            original_content = content

            # Remove any leading/trailing whitespace or non-JSON text
            content = content.strip()

            # Find the JSON object boundaries
            start = content.find("{")
            end = content.rfind("}")

            if start != -1 and end != -1 and end > start:
                content = content[start : end + 1]

                # Try to fix common issues
                import re

                # Fix single quotes to double quotes (but be careful with apostrophes in strings)
                # First, protect apostrophes in strings by temporarily replacing them
                content = re.sub(r"'([^']*)':", r'"\1":', content)  # Fix keys
                content = re.sub(
                    r":\s*'([^']*)'", r': "\1"', content
                )  # Fix string values
                content = re.sub(r"'\s*,", r'",', content)  # Fix trailing quotes
                content = re.sub(r"'\s*}", r'"}', content)  # Fix closing quotes
                content = re.sub(r"'\s*]", r'"]', content)  # Fix array closing quotes
                content = re.sub(r"\[\s*'", r'["', content)  # Fix array opening quotes
                content = re.sub(r"',\s*'", r'", "', content)  # Fix array separators

                # Fix trailing commas
                content = re.sub(r",(\s*[}\]])", r"\1", content)

                # Try parsing again
                try:
                    json.loads(content)
                    return content
                except json.JSONDecodeError:
                    # Try using ast.literal_eval to parse Python dict syntax, then convert to JSON
                    try:
                        import ast

                        # Get the original content and try to parse as Python dict
                        python_content = original_content[start : end + 1]
                        parsed_dict = ast.literal_eval(python_content)
                        return json.dumps(parsed_dict, indent=2)
                    except (ValueError, SyntaxError):
                        pass

            # If all else fails, return the current scene unchanged
            print(
                f"WARNING: Could not parse improved scene, keeping original. Error: {e}"
            )
            return current_expansion

    def analyze_story(self, story_context: str) -> str:
        """Analyze complete story for consistency and completeness for Step 9.5"""
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.story_analyzer(story_context=unique_context)

        # Clean up potential markdown formatting
        content = result.analysis_report.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        content = content.strip()

        return content
