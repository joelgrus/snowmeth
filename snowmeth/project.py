"""Project and story management for the Snowflake Method."""

import json
import re
from pathlib import Path
from typing import Optional, List

import click


class ProjectManager:
    """Manages multiple snowflake stories"""

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir)
        self.snowmeth_dir = self.project_dir / ".snowmeth"
        self.stories_dir = self.snowmeth_dir / "stories"
        self.config_file = self.snowmeth_dir / "config.json"

        # Ensure directories exist
        self.stories_dir.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load global config"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {"current_story": None}

    def _save_config(self):
        """Save global config"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    def _sanitize_slug(self, slug: str) -> str:
        """Convert slug to safe filename"""
        # Replace spaces and special chars with hyphens, lowercase
        sanitized = re.sub(r"[^a-zA-Z0-9\-_]", "-", slug.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r"-+", "-", sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip("-")

    def create_story(self, slug: str, story_idea: str) -> "Story":
        """Create a new story"""
        clean_slug = self._sanitize_slug(slug)
        story_file = self.stories_dir / f"{clean_slug}.json"

        if story_file.exists():
            raise click.ClickException(f"Story '{clean_slug}' already exists")

        story_data = {
            "slug": clean_slug,
            "story_idea": story_idea,
            "steps": {},
        }

        with open(story_file, "w") as f:
            json.dump(story_data, f, indent=2)

        # Set as current story
        self.config["current_story"] = clean_slug
        self._save_config()

        return Story(story_file)

    def get_current_story(self) -> Optional["Story"]:
        """Get the currently active story"""
        if not self.config["current_story"]:
            return None

        story_file = self.stories_dir / f"{self.config['current_story']}.json"
        if not story_file.exists():
            return None

        return Story(story_file)

    def switch_story(self, slug: str):
        """Switch to a different story"""
        clean_slug = self._sanitize_slug(slug)
        story_file = self.stories_dir / f"{clean_slug}.json"

        if not story_file.exists():
            raise click.ClickException(f"Story '{clean_slug}' not found")

        self.config["current_story"] = clean_slug
        self._save_config()

    def list_stories(self) -> List[dict]:
        """List all stories with basic info"""
        stories = []
        for story_file in self.stories_dir.glob("*.json"):
            try:
                with open(story_file, "r") as f:
                    data = json.load(f)
                stories.append(
                    {
                        "slug": data["slug"],
                        "story_idea": data["story_idea"],
                        "current": data["slug"] == self.config["current_story"],
                    }
                )
            except (json.JSONDecodeError, KeyError):
                continue
        return stories

    def delete_story(self, slug: str):
        """Delete a story"""
        clean_slug = self._sanitize_slug(slug)
        story_file = self.stories_dir / f"{clean_slug}.json"

        if not story_file.exists():
            raise click.ClickException(f"Story '{clean_slug}' not found")

        story_file.unlink()

        # If this was the current story, clear current
        if self.config["current_story"] == clean_slug:
            self.config["current_story"] = None
            self._save_config()


class Story:
    """Manages individual story data"""

    def __init__(self, story_file: Path):
        self.story_file = story_file
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Load story data from JSON file"""
        with open(self.story_file, "r") as f:
            data = json.load(f)

        # Remove deprecated current_step field for backward compatibility
        if "current_step" in data:
            del data["current_step"]

        return data

    def save(self):
        """Save story data to JSON file"""
        with open(self.story_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_step_content(self, step: int) -> Optional[str]:
        """Get content for a specific step"""
        return self.data["steps"].get(str(step), {}).get("content")

    def set_step_content(self, step: int, content: str):
        """Set content for a specific step"""
        if str(step) not in self.data["steps"]:
            self.data["steps"][str(step)] = {}
        self.data["steps"][str(step)]["content"] = content
        self.data["steps"][str(step)]["status"] = "complete"

    def get_current_step(self) -> int:
        """Get the current step (highest completed step)"""
        completed_steps = [
            int(step_num)
            for step_num, step_data in self.data["steps"].items()
            if step_data.get("content")
        ]
        return max(completed_steps) if completed_steps else 0

    def can_advance_to_step(self, step: int) -> bool:
        """Check if we can advance to a given step"""
        if step == 1:
            return True
        # Can only advance if previous step is complete
        prev_step = step - 1
        return self.get_step_content(prev_step) is not None

    def get_story_context(self, up_to_step: Optional[int] = None) -> str:
        """Build story context including original idea and completed steps"""
        if up_to_step is None:
            up_to_step = self.get_current_step()

        context_parts = [f"Original story idea: {self.data['story_idea']}"]

        # Add completed steps up to the specified step
        for step_num in range(1, up_to_step + 1):
            content = self.get_step_content(step_num)
            if content:
                step_names = {
                    1: "One-sentence summary",
                    2: "Paragraph summary",
                    3: "Character summaries",
                    4: "Plot summary",
                    5: "Character synopses",
                    6: "Detailed plot synopsis",
                    7: "Character charts",
                    8: "Scene breakdown",
                    9: "Scene expansions",
                }
                step_name = step_names.get(step_num, f"Step {step_num}")
                
                # Special formatting for Step 9 (scene expansions)
                if step_num == 9:
                    try:
                        import json
                        scenes = json.loads(content)
                        formatted_scenes = []
                        for scene_key, scene_data in scenes.items():
                            # Handle case where scene_data is a JSON string instead of dict
                            if isinstance(scene_data, str):
                                try:
                                    scene_data = json.loads(scene_data)
                                except json.JSONDecodeError:
                                    # If parsing fails, skip this scene
                                    continue
                            
                            # Skip if scene_data is still not a dict
                            if not isinstance(scene_data, dict):
                                continue
                                
                            scene_num = scene_data.get('scene_number', scene_key)
                            title = scene_data.get('title', 'Untitled')
                            pov = scene_data.get('pov_character', 'Unknown')
                            goal = scene_data.get('scene_goal', 'No goal specified')
                            motivation = scene_data.get('character_motivation', 'No motivation specified')
                            beats = scene_data.get('key_beats', [])
                            
                            scene_summary = f"Scene {scene_num}: '{title}' (POV: {pov})\n"
                            scene_summary += f"  Goal: {goal}\n"
                            scene_summary += f"  Character Motivation: {motivation}\n"
                            if beats:
                                scene_summary += f"  Key Beats: {'; '.join(beats[:3])}{'...' if len(beats) > 3 else ''}"
                            
                            formatted_scenes.append(scene_summary)
                        
                        formatted_content = "\n\n".join(formatted_scenes)
                        context_parts.append(f"{step_name}:\n{formatted_content}")
                    except (json.JSONDecodeError, KeyError):
                        # Fallback to raw content if parsing fails
                        context_parts.append(f"{step_name}: {content}")
                else:
                    context_parts.append(f"{step_name}: {content}")

        return "\n\n".join(context_parts)
