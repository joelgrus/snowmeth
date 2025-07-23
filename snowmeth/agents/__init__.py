"""Snowflake Method AI agents module."""

# Import the compatibility wrapper to maintain existing API
from .compatibility import SnowflakeAgent

# Import individual agents for direct use
from .sentence_summary import SentenceSummaryAgent
from .paragraph_expansion import ParagraphExpansionAgent
from .character_extraction import CharacterExtractionAgent
from .plot_expansion import PlotExpansionAgent
from .character_synopses import CharacterSynopsesAgent
from .detailed_plot import DetailedPlotAgent
from .character_charts import CharacterChartsAgent
from .scene_breakdown import SceneBreakdownAgent
from .scene_expansion import SceneExpansionAgent
from .chapter_writer import ChapterWriterAgent

# Import shared models and utilities
from .shared_models import ContentRefiner, clean_json_markdown

__all__ = [
    "SnowflakeAgent",  # Main compatibility wrapper
    "SentenceSummaryAgent",
    "ParagraphExpansionAgent", 
    "CharacterExtractionAgent",
    "PlotExpansionAgent",
    "CharacterSynopsesAgent",
    "DetailedPlotAgent",
    "CharacterChartsAgent",
    "SceneBreakdownAgent",
    "SceneExpansionAgent",
    "ChapterWriterAgent",
    "ContentRefiner",
    "clean_json_markdown",
]