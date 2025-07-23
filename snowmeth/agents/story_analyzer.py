"""Agent for Step 9.5: Analyze the complete story for consistency and completeness."""

import json
import random
import dspy
from typing import List, Dict
from pydantic import BaseModel, Field


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


class StoryAnalyzer(dspy.Signature):
    """Analyze the complete story for consistency, POV distribution, subplot tracking, and narrative completeness"""

    story_context: str = dspy.InputField(
        desc="Complete story context including all steps 1-9, especially detailed scene expansions from Step 9"
    )
    analysis_report: StoryAnalysis = dspy.OutputField(
        desc="Provide a comprehensive analysis of the story covering POV distribution, character development, subplot tracking, story structure, consistency checks, completeness analysis, and prioritized recommendations for improvement."
    )


class StoryAnalyzerAgent(dspy.Module):
    """Agent for analyzing story consistency and completeness (Step 9.5)."""

    def __init__(self):
        super().__init__()
        self.story_analyzer = dspy.ChainOfThought(StoryAnalyzer)

    def __call__(self, story_context: str) -> str:
        """Analyze complete story for consistency and completeness.

        Args:
            story_context: Complete story context including all steps 1-9

        Returns:
            JSON string containing comprehensive story analysis
        """
        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"
        result = self.story_analyzer(story_context=unique_context)

        # Convert the structured output to JSON format expected by the system
        return json.dumps(result.analysis_report.dict(), indent=2)
