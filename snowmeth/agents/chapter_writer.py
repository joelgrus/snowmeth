"""Agent for Step 10: Write full chapter prose based on scene expansions."""

import random
import dspy
import dspy.streaming
from typing import List, Dict, Any, AsyncGenerator


class ChapterWriter(dspy.Signature):
    """Write a complete novel chapter based on the provided scene expansion and context.

    CRITICAL REQUIREMENTS:
    - Write a substantial novel chapter (3,000-5,000 words minimum)
    - This should be a complete chapter with full scenes and development
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

    LENGTH IS CRITICAL: This must be a complete chapter with full scenes, dialogue, and narrative.
    Write engaging, detailed prose that brings the scene expansion to life with concrete details and character development.

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
        desc="Complete novel chapter prose (3,000-5,000 words, NO markdown headers, start directly with story content). Begin immediately with the first sentence of the chapter. Write the full chapter with dialogue, action, description, and character development."
    )


class ChapterRefiner(dspy.Signature):
    """Refine an existing novel chapter based on specific instructions.

    CRITICAL REQUIREMENTS:
    - Keep the chapter substantial (3,000-5,000 words) - do not shorten it significantly
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
    current_content = dspy.InputField(desc="The current chapter content to be refined")
    refinement_instructions = dspy.InputField(
        desc="Specific instructions for how to refine the chapter"
    )
    refined_chapter = dspy.OutputField(
        desc="The refined chapter with improvements applied (3,000-5,000 words, NO markdown headers)"
    )


class ChapterWriterAgent(dspy.Module):
    """Agent for writing full chapter prose (Step 10)."""

    def __init__(self):
        super().__init__()
        self.chapter_writer = dspy.ChainOfThought(ChapterWriter)
        self.chapter_refiner = dspy.ChainOfThought(ChapterRefiner)

    def generate(
        self,
        story_context: str,
        scene_data: Dict[str, Any],
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        writing_style: str = "",
        previous_chapter_content: str = None,
    ) -> str:
        """Generate full chapter prose based on scene expansion data.

        Args:
            story_context: Complete story context including all previous steps
            scene_data: Detailed scene expansion data
            chapter_number: The chapter number being written
            previous_chapters: List of previous chapter summaries
            writing_style: Specific writing style instructions
            previous_chapter_content: Content of previous chapter for style matching

        Returns:
            Complete chapter prose
        """
        # Prepare previous chapters context
        prev_chapters_text = ""
        if previous_chapters:
            prev_chapters_text = "\n\nPrevious Chapters:\n"
            for ch in previous_chapters:
                prev_chapters_text += (
                    f"Chapter {ch['chapter_number']}: {ch['summary']}\n"
                )

        # Prepare scene expansion details
        scene_text = self._format_scene_expansion(scene_data, chapter_number)

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Prepare writing style instructions
        style_instructions = (
            writing_style.strip()
            if writing_style
            else "Write in clear, engaging prose suitable for a novel."
        )

        # Prepare previous chapter content for style matching
        prev_chapter_sample = self._prepare_chapter_sample(previous_chapter_content)

        # Generate the chapter
        result = self.chapter_writer(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            previous_chapters=prev_chapters_text,
            writing_style=style_instructions,
            previous_chapter_sample=prev_chapter_sample,
        )

        return result.chapter_prose

    def refine(
        self,
        story_context: str,
        chapter_number: int,
        current_content: str,
        scene_data: Dict[str, Any],
        instructions: str,
    ) -> str:
        """Refine an existing chapter with specific instructions.

        Args:
            story_context: Complete story context
            chapter_number: The chapter number being refined
            current_content: Current chapter content
            scene_data: Scene expansion data
            instructions: Refinement instructions

        Returns:
            Refined chapter prose
        """
        # Prepare scene expansion details
        scene_text = self._format_scene_expansion(scene_data, chapter_number)

        # Add randomness to avoid caching
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Refine the chapter
        result = self.chapter_refiner(
            story_context=unique_context,
            scene_expansion=scene_text,
            chapter_number=str(chapter_number),
            current_content=current_content,
            refinement_instructions=instructions,
        )

        return result.refined_chapter

    async def generate_stream(
        self,
        story_context: str,
        scene_data: Dict[str, Any],
        chapter_number: int,
        previous_chapters: List[Dict[str, Any]],
        writing_style: str = "",
        previous_chapter_content: str = None,
    ) -> AsyncGenerator[str, None]:
        """Generate full chapter prose with streaming support.

        Args:
            story_context: Complete story context including all previous steps
            scene_data: Detailed scene expansion data
            chapter_number: The chapter number being written
            previous_chapters: List of previous chapter summaries
            writing_style: Specific writing style instructions
            previous_chapter_content: Content of previous chapter for style matching

        Yields:
            Chapter prose chunks
        """
        # Prepare all inputs (same as generate method)
        prev_chapters_text = ""
        if previous_chapters:
            prev_chapters_text = "\n\nPrevious Chapters:\n"
            for ch in previous_chapters:
                prev_chapters_text += (
                    f"Chapter {ch['chapter_number']}: {ch['summary']}\n"
                )

        scene_text = self._format_scene_expansion(scene_data, chapter_number)
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        style_instructions = (
            writing_style.strip()
            if writing_style
            else "Write in clear, engaging prose suitable for a novel."
        )

        prev_chapter_sample = self._prepare_chapter_sample(previous_chapter_content)

        # Wrap the chapter writer with streaming support
        stream_writer = dspy.streamify(
            self.chapter_writer,
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

    async def refine_stream(
        self,
        story_context: str,
        chapter_number: int,
        current_content: str,
        scene_data: Dict[str, Any],
        instructions: str,
    ) -> AsyncGenerator[str, None]:
        """Refine an existing chapter with streaming support.

        Args:
            story_context: Complete story context
            chapter_number: The chapter number being refined
            current_content: Current chapter content
            scene_data: Scene expansion data
            instructions: Refinement instructions

        Yields:
            Refined chapter prose chunks
        """
        # Prepare scene expansion details
        scene_text = self._format_scene_expansion(scene_data, chapter_number)
        unique_context = f"{story_context} [seed: {random.randint(1000, 9999)}]"

        # Wrap the chapter refiner with streaming support
        stream_refiner = dspy.streamify(
            self.chapter_refiner,
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
                yield chunk.chunk

    def _format_scene_expansion(
        self, scene_data: Dict[str, Any], chapter_number: int
    ) -> str:
        """Format scene expansion data into text for the prompts."""
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

        return scene_text

    def _prepare_chapter_sample(self, previous_chapter_content: str) -> str:
        """Prepare previous chapter content for style matching."""
        if previous_chapter_content:
            # Limit to first 2000 characters to avoid token limits while providing style sample
            return (
                previous_chapter_content[:2000] + "..."
                if len(previous_chapter_content) > 2000
                else previous_chapter_content
            )
        else:
            return "No previous chapter available - this is the first chapter."
