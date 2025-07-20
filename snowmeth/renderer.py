"""Display and formatting logic for stories and content."""

import json
from typing import List, Dict, Any

from .project import Story


class StoryRenderer:
    """Handles formatting and display of story content"""

    def format_story_list(self, stories: List[Dict[str, Any]]) -> str:
        """Format a list of stories for display"""
        if not stories:
            return "No stories found. Use 'snowmeth new <slug> <story_idea>' to create one."

        lines = ["Stories:"]
        for story in stories:
            marker = "→" if story["current"] else " "
            lines.append(f"  {marker} {story['slug']}: {story['story_idea']}")

        return "\n".join(lines)

    def format_story_overview(self, story: Story) -> str:
        """Format complete story overview with all steps"""
        lines = [
            f"Current story: {story.data['slug']}",
            f"Story idea: {story.data['story_idea']}",
            f"Current step: {story.get_current_step()}",
        ]

        # Add each completed step
        lines.extend(self._format_step_content(story, 1, "One-sentence summary"))
        lines.extend(self._format_step_content(story, 2, "Paragraph summary"))
        lines.extend(self._format_step_content(story, 3, "Character summaries"))
        lines.extend(self._format_step_content(story, 4, "Plot summary"))
        lines.extend(self._format_step_content(story, 5, "Character synopses"))
        lines.extend(self._format_step_content(story, 6, "Detailed plot synopsis"))
        lines.extend(self._format_step_content(story, 7, "Character charts"))
        lines.extend(self._format_step_content(story, 8, "Scene breakdown"))

        # Add next step hint
        hint = self._get_next_step_hint(story)
        if hint:
            lines.extend(["", hint])

        return "\n".join(lines)

    def _format_step_content(
        self, story: Story, step_num: int, title: str
    ) -> List[str]:
        """Format content for a specific step"""
        content = story.get_step_content(step_num)
        if not content:
            return []

        lines = [f"\nStep {step_num} - {title}:"]

        if step_num == 1:
            # Sentence gets quotes
            lines.append(f"'{content}'")
        elif step_num == 3 or step_num == 5 or step_num == 7:
            # Characters, character synopses, and character charts get special formatting
            lines.extend(self._format_characters(content))
        elif step_num == 8:
            # Scene breakdown gets special formatting
            lines.extend(self._format_scene_breakdown(content))
        else:
            # Regular content
            lines.append(content)

        return lines

    def _format_characters(self, characters_content: str) -> List[str]:
        """Format character summaries with proper indentation"""
        lines = []
        try:
            char_dict = json.loads(characters_content)
            for i, (name, summary) in enumerate(char_dict.items()):
                if i > 0:
                    lines.append("")  # Blank line between characters
                lines.append(f"  • {name}:")
                # Indent the character summary
                for line in summary.split("\n"):
                    lines.append(f"    {line}")
        except (json.JSONDecodeError, AttributeError):
            # Fallback if not valid JSON
            lines.append(characters_content)

        return lines

    def _format_scene_breakdown(self, scene_content: str) -> List[str]:
        """Format scene breakdown with proper table-like formatting"""
        lines = []
        try:
            # Clean up potential markdown formatting
            content = scene_content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
            content = content.strip()

            scenes = json.loads(content)
            if not isinstance(scenes, list):
                raise ValueError("Scene breakdown should be a list")

            # Add header
            lines.append(
                "  Scene | POV Character      | Description                                    | Pages"
            )
            lines.append(
                "  ------|--------------------|-------------------------------------------------|------"
            )

            for scene in scenes:
                scene_num = str(scene.get("scene_number", "?")).rjust(5)
                pov = scene.get("pov_character", "Unknown")[:18].ljust(18)
                desc = scene.get("scene_description", "No description")[:47].ljust(47)
                pages = str(scene.get("estimated_pages", "?")).rjust(5)

                lines.append(f"  {scene_num} | {pov} | {desc} | {pages}")

        except (json.JSONDecodeError, ValueError, AttributeError):
            # Fallback if not valid JSON
            lines.append(scene_content)

        return lines

    def _get_next_step_hint(self, story: Story) -> str:
        """Get hint for next available step"""
        current_step = story.get_current_step()

        hints = {
            1: "💡 Ready for next step? Use 'snowmeth next' to expand to paragraph.",
            2: "💡 Ready for next step? Use 'snowmeth next' to extract characters.",
            3: "💡 Ready for next step? Use 'snowmeth next' to expand plot.",
            4: "💡 Ready for next step? Use 'snowmeth next' to generate character synopses.",
            5: "💡 Ready for next step? Use 'snowmeth next' to expand to detailed plot synopsis.",
            6: "💡 Ready for next step? Use 'snowmeth next' to generate detailed character charts.",
            7: "💡 Ready for next step? Use 'snowmeth next' to generate scene breakdown.",
            8: "💡 Congratulations! You've completed the core Snowflake Method steps.",
        }

        # Only show hint if current step is complete
        if story.get_step_content(current_step):
            return hints.get(current_step, "")

        return ""

    def format_step_content_for_editing(self, story: Story, step_num: int) -> str:
        """Format step content for editing/refinement display"""
        content = story.get_step_content(step_num)
        if not content:
            return f"No content found for step {step_num}."

        step_types = {
            1: "sentence",
            2: "paragraph",
            3: "character",
            4: "plot",
            5: "character_synopsis",
            6: "detailed_plot",
            7: "character_chart",
            8: "scene_breakdown",
        }
        content_type = step_types.get(step_num, f"step-{step_num}")

        lines = [f"Current step {step_num} ({content_type}):"]

        if step_num == 1:
            lines.append(f"  '{content}'")
        else:
            lines.append(content)

        return "\n".join(lines)

    def format_generated_content(self, content: str, step_num: int, title: str) -> str:
        """Format newly generated content for display"""
        lines = [f"\n{title}:"]

        if step_num == 1:
            lines.append(f"  '{content}'")
        else:
            lines.append(content)

        return "\n".join(lines)

    def format_system_status(
        self,
        model: str,
        has_key: bool,
        key_info: str,
        stories_count: int,
        current_story_slug: str = None,
    ) -> str:
        """Format system status display"""
        lines = ["Snowmeth System Status:", "=" * 25, f"✓ Default model: {model}"]

        if has_key:
            lines.append(f"✓ API Key: {key_info}")
        else:
            lines.append(f"✗ API Key: {key_info}")

        lines.append(f"✓ Stories found: {stories_count}")

        if current_story_slug:
            lines.append(f"✓ Current story: {current_story_slug}")
        elif stories_count > 0:
            lines.append("✗ No current story selected")

        status_msg = (
            "Ready to use snowmeth!" if has_key else "Set API key to use AI features."
        )
        lines.extend(["", status_msg])

        return "\n".join(lines)

    def format_model_list(self, models: Dict[str, str], llm_config) -> str:
        """Format configured models list"""
        lines = ["Configured Models:", "=" * 18]

        for step, model in models.items():
            has_key, _ = llm_config.check_api_key(model)
            status = "✓" if has_key else "✗"
            lines.append(f"  {step}: {model} {status}")

        lines.extend(
            [
                "",
                "Example models:",
                "  openai/gpt-4o-mini",
                "  openai/gpt-4o",
                "  openrouter/google/gemini-2.5-flash-lite-preview-06-17",
                "  openrouter/google/gemini-2.5-pro-preview",
            ]
        )

        return "\n".join(lines)
