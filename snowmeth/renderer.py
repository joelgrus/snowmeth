"""Display and formatting logic for stories and content."""

import json
from typing import List, Dict, Any

from .storage import Story


class StoryRenderer:
    """Handles formatting and display of story content"""

    def format_story_list(self, stories: List[Story], current_story_id: str = None) -> str:
        """Format a list of stories for display"""
        if not stories:
            return "No stories found. Use 'snowmeth new <slug> <story_idea>' to create one."

        lines = ["Stories:"]
        for story in stories:
            # Check if this is the current story
            is_current = (current_story_id and 
                         (story.story_id == current_story_id or story.slug == current_story_id))
            marker = "→" if is_current else " "
            story_idea = story.data.get('story_idea', 'No story idea')
            lines.append(f"  {marker} {story.slug}: {story_idea}")

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
        lines.extend(self._format_step_content(story, 9, "Scene expansions"))
        lines.extend(self._format_step_content(story, 9.5, "Story analysis"))

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
        elif step_num == 9:
            # Scene expansions get special formatting
            lines.extend(self._format_scene_expansions(content))
        elif step_num == 9.5:
            # Story analysis gets special formatting
            lines.extend(self._format_story_analysis(content))
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

    def _format_scene_expansions(self, expansions_content: str) -> List[str]:
        """Format scene expansions with detailed mini-outlines"""
        lines = []
        try:
            # Clean up potential markdown formatting
            content = expansions_content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
            content = content.strip()

            expansions = json.loads(content)
            if not isinstance(expansions, dict):
                raise ValueError("Scene expansions should be a dictionary")

            for scene_key, expansion in expansions.items():
                if lines:  # Add blank line between scenes
                    lines.append("")
                
                # Scene header
                scene_num = expansion.get("scene_number", "?")
                title = expansion.get("title", "Untitled Scene")
                pov = expansion.get("pov_character", "Unknown")
                lines.append(f"  Scene {scene_num}: {title} (POV: {pov})")
                lines.append("  " + "=" * 50)
                
                # Setting
                setting = expansion.get("setting", "")
                if setting:
                    lines.append(f"  Setting: {setting}")
                
                # Goals and motivation
                scene_goal = expansion.get("scene_goal", "")
                char_goal = expansion.get("character_goal", "")
                motivation = expansion.get("character_motivation", "")
                
                if scene_goal:
                    lines.append(f"  Scene Goal: {scene_goal}")
                if char_goal:
                    lines.append(f"  Character Goal: {char_goal}")
                if motivation:
                    lines.append(f"  Motivation: {motivation}")
                
                # Conflict and obstacles
                obstacles = expansion.get("obstacles", "")
                conflict_type = expansion.get("conflict_type", "")
                
                if obstacles:
                    lines.append(f"  Obstacles: {obstacles}")
                if conflict_type:
                    lines.append(f"  Conflict: {conflict_type}")
                
                # Key beats
                key_beats = expansion.get("key_beats", [])
                if key_beats:
                    lines.append("  Key Beats:")
                    for beat in key_beats:
                        lines.append(f"    • {beat}")
                
                # Emotional arc and outcome
                emotional_arc = expansion.get("emotional_arc", "")
                outcome = expansion.get("scene_outcome", "")
                
                if emotional_arc:
                    lines.append(f"  Emotional Arc: {emotional_arc}")
                if outcome:
                    lines.append(f"  Outcome: {outcome}")
                
                # Advanced features
                subplots = expansion.get("subplot_elements", [])
                relationships = expansion.get("character_relationships", "")
                foreshadowing = expansion.get("foreshadowing", "")
                
                if subplots:
                    lines.append("  Subplot Elements:")
                    for subplot in subplots:
                        lines.append(f"    • {subplot}")
                
                if relationships:
                    lines.append(f"  Character Relationships: {relationships}")
                
                if foreshadowing:
                    lines.append(f"  Foreshadowing: {foreshadowing}")
                
                # Page estimate
                pages = expansion.get("estimated_pages", "?")
                lines.append(f"  Estimated Pages: {pages}")

        except (json.JSONDecodeError, ValueError, AttributeError):
            # Fallback if not valid JSON
            lines.append(expansions_content)

        return lines

    def _format_story_analysis(self, analysis_content: str) -> List[str]:
        """Format story analysis with detailed breakdown"""
        lines = []
        try:
            # Clean up potential markdown formatting
            content = analysis_content.strip()
            if content.startswith("```json"):
                content = content[7:]  # Remove ```json
            if content.endswith("```"):
                content = content[:-3]  # Remove ```
            content = content.strip()

            analysis = json.loads(content)
            if not isinstance(analysis, dict):
                raise ValueError("Story analysis should be a dictionary")

            # Overall Assessment
            overall = analysis.get("overall_assessment", {})
            if overall:
                lines.append("  📊 OVERALL ASSESSMENT")
                lines.append("  " + "=" * 50)
                
                readiness = overall.get("readiness_score", "N/A")
                lines.append(f"  Readiness Score: {readiness}/10")
                
                strengths = overall.get("strengths", [])
                if strengths:
                    lines.append("  ✅ Strengths:")
                    for strength in strengths:
                        lines.append(f"    • {strength}")
                
                weaknesses = overall.get("weaknesses", [])
                if weaknesses:
                    lines.append("  ⚠️  Weaknesses:")
                    for weakness in weaknesses:
                        lines.append(f"    • {weakness}")
                lines.append("")

            # POV Analysis
            pov_analysis = analysis.get("pov_analysis", {})
            if pov_analysis:
                lines.append("  👁️  POV ANALYSIS")
                lines.append("  " + "=" * 50)
                
                distribution = pov_analysis.get("distribution", {})
                if distribution:
                    lines.append("  Scene Distribution:")
                    for character, count in distribution.items():
                        lines.append(f"    • {character}: {count} scenes")
                
                issues = pov_analysis.get("issues", [])
                if issues:
                    lines.append("  Issues:")
                    for issue in issues:
                        lines.append(f"    ⚠️  {issue}")
                
                recommendations = pov_analysis.get("recommendations", [])
                if recommendations:
                    lines.append("  Recommendations:")
                    for rec in recommendations:
                        lines.append(f"    💡 {rec}")
                lines.append("")

            # Character Analysis
            char_analysis = analysis.get("character_analysis", {})
            if char_analysis:
                lines.append("  👥 CHARACTER ANALYSIS")
                lines.append("  " + "=" * 50)
                
                forgotten = char_analysis.get("forgotten_characters", [])
                if forgotten:
                    lines.append("  Forgotten Characters:")
                    for char in forgotten:
                        lines.append(f"    ⚠️  {char}")
                
                arc_issues = char_analysis.get("character_arc_issues", [])
                if arc_issues:
                    lines.append("  Character Arc Issues:")
                    for issue in arc_issues:
                        lines.append(f"    ⚠️  {issue}")
                
                relationship_issues = char_analysis.get("relationship_tracking", [])
                if relationship_issues:
                    lines.append("  Relationship Issues:")
                    for issue in relationship_issues:
                        lines.append(f"    ⚠️  {issue}")
                lines.append("")

            # Subplot Analysis
            subplot_analysis = analysis.get("subplot_analysis", {})
            if subplot_analysis:
                lines.append("  🧵 SUBPLOT ANALYSIS")
                lines.append("  " + "=" * 50)
                
                identified = subplot_analysis.get("identified_subplots", [])
                if identified:
                    lines.append("  Identified Subplots:")
                    for subplot in identified:
                        lines.append(f"    • {subplot}")
                
                incomplete = subplot_analysis.get("incomplete_subplots", [])
                if incomplete:
                    lines.append("  Incomplete Subplots:")
                    for subplot in incomplete:
                        lines.append(f"    ⚠️  {subplot}")
                
                resolution_issues = subplot_analysis.get("resolution_issues", [])
                if resolution_issues:
                    lines.append("  Resolution Issues:")
                    for issue in resolution_issues:
                        lines.append(f"    ⚠️  {issue}")
                lines.append("")

            # Story Structure
            structure = analysis.get("story_structure", {})
            if structure:
                lines.append("  🏗️  STORY STRUCTURE")
                lines.append("  " + "=" * 50)
                
                pacing_issues = structure.get("pacing_issues", [])
                if pacing_issues:
                    lines.append("  Pacing Issues:")
                    for issue in pacing_issues:
                        lines.append(f"    ⚠️  {issue}")
                
                plot_holes = structure.get("plot_holes", [])
                if plot_holes:
                    lines.append("  Plot Holes:")
                    for hole in plot_holes:
                        lines.append(f"    ⚠️  {hole}")
                
                foreshadowing = structure.get("foreshadowing_analysis", [])
                if foreshadowing:
                    lines.append("  Foreshadowing Analysis:")
                    for item in foreshadowing:
                        lines.append(f"    💡 {item}")
                lines.append("")

            # Consistency Checks
            consistency = analysis.get("consistency_checks", {})
            if consistency:
                lines.append("  🔍 CONSISTENCY CHECKS")
                lines.append("  " + "=" * 50)
                
                timeline_issues = consistency.get("timeline_issues", [])
                if timeline_issues:
                    lines.append("  Timeline Issues:")
                    for issue in timeline_issues:
                        lines.append(f"    ⚠️  {issue}")
                
                setting_issues = consistency.get("setting_consistency", [])
                if setting_issues:
                    lines.append("  Setting Consistency:")
                    for issue in setting_issues:
                        lines.append(f"    ⚠️  {issue}")
                
                voice_issues = consistency.get("character_voice", [])
                if voice_issues:
                    lines.append("  Character Voice Issues:")
                    for issue in voice_issues:
                        lines.append(f"    ⚠️  {issue}")
                lines.append("")

            # Recommendations
            recommendations = analysis.get("recommendations", {})
            if recommendations:
                lines.append("  🎯 RECOMMENDATIONS")
                lines.append("  " + "=" * 50)
                
                high_priority = recommendations.get("high_priority", [])
                if high_priority:
                    lines.append("  🔴 High Priority:")
                    for rec in high_priority:
                        lines.append(f"    • {rec}")
                
                medium_priority = recommendations.get("medium_priority", [])
                if medium_priority:
                    lines.append("  🟡 Medium Priority:")
                    for rec in medium_priority:
                        lines.append(f"    • {rec}")
                
                low_priority = recommendations.get("low_priority", [])
                if low_priority:
                    lines.append("  🟢 Low Priority:")
                    for rec in low_priority:
                        lines.append(f"    • {rec}")

        except (json.JSONDecodeError, ValueError, AttributeError):
            # Fallback if not valid JSON
            lines.append(analysis_content)

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
            8: "💡 Ready for next step? Use 'snowmeth next' to expand scenes into detailed mini-outlines.",
            9: "💡 Ready for next step? Use 'snowmeth next' to analyze story for consistency and completeness.",
            9.5: "💡 Congratulations! You've completed the extended Snowflake Method with analysis.",
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
            9: "scene_expansion",
            9.5: "story_analysis",
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
