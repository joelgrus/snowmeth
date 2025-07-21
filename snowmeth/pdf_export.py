"""PDF export functionality for Snowflake Method stories."""

import json
from datetime import datetime
from fpdf import FPDF
from .storage import Story


class StoryPDF(FPDF):
    """Custom PDF class for Snowflake Method story documents."""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Add header to each page."""
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "Snowflake Method - Story Plan", 0, 1, "C")
        self.ln(10)

    def footer(self):
        """Add footer to each page."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title: str):
        """Add a chapter title."""
        self.add_page()
        self.set_font("Arial", "B", 16)
        normalized_title = self._normalize_unicode(title)
        self.cell(0, 10, normalized_title, 0, 1, "L")
        self.ln(5)

    def section_title(self, title: str):
        """Add a section title."""
        self.ln(5)
        self.set_font("Arial", "B", 14)
        normalized_title = self._normalize_unicode(title)
        self.cell(0, 10, normalized_title, 0, 1, "L")
        self.ln(2)

    def add_text(self, text: str):
        """Add formatted text content."""
        self.set_font("Arial", "", 11)
        # Handle text wrapping with Unicode normalization
        normalized_text = self._normalize_unicode(text)
        self.multi_cell(0, 6, normalized_text)
        self.ln(3)
    
    def _normalize_unicode(self, text: str) -> str:
        """Normalize Unicode characters for PDF compatibility."""
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '\u2019': "'",  # Right single quotation mark
            '\u2018': "'",  # Left single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2026': '...',# Horizontal ellipsis
            '\u2022': '*',  # Bullet point
            '\u00a0': ' ',  # Non-breaking space
            '\u00b7': '*',  # Middle dot
        }
        
        normalized = text
        for unicode_char, replacement in replacements.items():
            normalized = normalized.replace(unicode_char, replacement)
        
        # Remove any remaining non-ASCII characters
        try:
            normalized.encode('latin-1')
            return normalized
        except UnicodeEncodeError:
            # If we still have Unicode issues, encode and decode to clean it
            return normalized.encode('ascii', 'ignore').decode('ascii')
        
        return normalized

    def add_character_list(self, characters_json: str):
        """Add character list with formatting."""
        try:
            clean_content = self._clean_json_content(characters_json)
            characters = json.loads(clean_content)
            for name, description in characters.items():
                self.section_title(f"Character: {name}")
                self.add_text(description)
        except (json.JSONDecodeError, AttributeError):
            self.add_text(characters_json)

    def _clean_json_content(self, content: str) -> str:
        """Clean JSON content from markdown code blocks."""
        clean_content = content.strip()
        
        # Remove markdown code blocks if present
        if clean_content.startswith('```json') and clean_content.endswith('```'):
            clean_content = clean_content[7:-3].strip()
        elif clean_content.startswith('```') and clean_content.endswith('```'):
            clean_content = clean_content[3:-3].strip()
            
        return clean_content

    def add_scene_list(self, scenes_json: str):
        """Add scene list with formatting."""
        try:
            clean_content = self._clean_json_content(scenes_json)
            scenes = json.loads(clean_content)
            
            # Handle different possible structures
            if isinstance(scenes, list):
                # Direct list of scenes
                for i, scene in enumerate(scenes, 1):
                    if isinstance(scene, dict):
                        scene_num = scene.get('scene_number', scene.get('id', i))
                        pov = scene.get('pov_character', scene.get('character', 'Unknown POV'))
                        scene_title = f"Scene {scene_num}: {pov}"
                        self.section_title(scene_title)
                        
                        description = scene.get("scene_description", scene.get("description", ""))
                        if description:
                            self.add_text(description)
                        
                        pages = scene.get("estimated_pages", scene.get("pages", 0))
                        if pages:
                            self.set_font("Arial", "I", 10)
                            self.cell(0, 5, f"Estimated pages: {pages}", 0, 1)
                            self.ln(2)
                    else:
                        # Scene is not a dict, just add it as text
                        self.add_text(str(scene))
                        
            elif isinstance(scenes, dict):
                # Dictionary of scenes (might be keyed by scene number)
                for key, scene_data in scenes.items():
                    if isinstance(scene_data, dict):
                        scene_num = scene_data.get('scene_number', key)
                        pov = scene_data.get('pov_character', scene_data.get('character', 'Unknown POV'))
                        scene_title = f"Scene {scene_num}: {pov}"
                        self.section_title(scene_title)
                        
                        description = scene_data.get("scene_description", scene_data.get("description", ""))
                        if description:
                            self.add_text(description)
                        
                        pages = scene_data.get("estimated_pages", scene_data.get("pages", 0))
                        if pages:
                            self.set_font("Arial", "I", 10)
                            self.cell(0, 5, f"Estimated pages: {pages}", 0, 1)
                            self.ln(2)
                    else:
                        # Scene data is not a dict
                        self.section_title(f"Scene {key}")
                        self.add_text(str(scene_data))
            else:
                # Neither list nor dict, just add as text
                self.add_text(str(scenes))
                
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            # If JSON parsing fails, add raw text with a note
            self.section_title("Scene List (Raw Data)")
            self.add_text(f"Note: Could not parse scene data structure.\n\n{scenes_json}")

    def add_scene_expansions(self, expansions_json: str):
        """Add scene expansions with detailed formatting."""
        try:
            clean_content = self._clean_json_content(expansions_json)
            expansions = json.loads(clean_content)
            for scene_key, scene_data in expansions.items():
                scene_num = scene_data.get("scene_number", "Unknown")
                title = scene_data.get("title", f"Scene {scene_num}")

                self.section_title(f"Scene {scene_num}: {title}")

                # Basic info
                pov = scene_data.get("pov_character", "Unknown")
                pages = scene_data.get("estimated_pages", 0)
                self.add_text(f"POV Character: {pov} | Estimated Pages: {pages}")

                # Setting
                setting = scene_data.get("setting", "")
                if setting:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Setting:", 0, 1)
                    self.add_text(setting)

                # Goals and motivation
                scene_goal = scene_data.get("scene_goal", "")
                char_goal = scene_data.get("character_goal", "")
                motivation = scene_data.get("character_motivation", "")

                if scene_goal:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Scene Goal:", 0, 1)
                    self.add_text(scene_goal)

                if char_goal:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Character Goal:", 0, 1)
                    self.add_text(char_goal)

                if motivation:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Character Motivation:", 0, 1)
                    self.add_text(motivation)

                # Obstacles and conflict
                obstacles = scene_data.get("obstacles", [])
                if obstacles:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Obstacles:", 0, 1)
                    for obstacle in obstacles:
                        self.set_font("Arial", "", 11)
                        normalized_obstacle = self._normalize_unicode(f"* {obstacle}")
                        self.cell(0, 6, normalized_obstacle, 0, 1)
                    self.ln(2)

                conflict = scene_data.get("conflict_type", "")
                if conflict:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Conflict Type:", 0, 1)
                    self.add_text(conflict)

                # Key beats
                key_beats = scene_data.get("key_beats", [])
                if key_beats:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Key Story Beats:", 0, 1)
                    for beat in key_beats:
                        self.set_font("Arial", "", 11)
                        normalized_beat = self._normalize_unicode(f"* {beat}")
                        self.cell(0, 6, normalized_beat, 0, 1)
                    self.ln(2)

                # Emotional arc and outcome
                emotional_arc = scene_data.get("emotional_arc", "")
                if emotional_arc:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Emotional Arc:", 0, 1)
                    self.add_text(emotional_arc)

                outcome = scene_data.get("scene_outcome", "")
                if outcome:
                    self.set_font("Arial", "B", 11)
                    self.cell(0, 6, "Scene Outcome:", 0, 1)
                    self.add_text(outcome)

                self.ln(5)  # Extra space between scenes

        except (json.JSONDecodeError, AttributeError):
            self.add_text(expansions_json)


def generate_story_pdf(story: Story) -> bytes:
    """Generate a comprehensive PDF document for the story."""
    pdf = StoryPDF()

    # Cover page
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, story.slug.replace("-", " ").title(), 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "I", 14)
    pdf.cell(0, 10, "Snowflake Method Story Plan", 0, 1, "C")
    pdf.ln(20)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%B %d, %Y')}", 0, 1, "C")

    # Story idea
    story_idea = story.data.get("story_idea", "")
    if story_idea:
        pdf.ln(20)
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Story Idea:", 0, 1, "L")
        pdf.add_text(story_idea)

    # Step 1: One Sentence Summary
    step1_content = story.get_step_content(1)
    if step1_content:
        pdf.chapter_title("Step 1: One Sentence Summary")
        pdf.add_text(step1_content)

    # Step 2: One Paragraph Summary
    step2_content = story.get_step_content(2)
    if step2_content:
        pdf.chapter_title("Step 2: One Paragraph Summary")
        pdf.add_text(step2_content)

    # Step 3: Characters
    step3_content = story.get_step_content(3)
    if step3_content:
        pdf.chapter_title("Step 3: Character Summaries")
        pdf.add_character_list(step3_content)

    # Step 4: Story Structure
    step4_content = story.get_step_content(4)
    if step4_content:
        pdf.chapter_title("Step 4: Story Structure")
        pdf.add_text(step4_content)

    # Step 5: Character Synopses
    step5_content = story.get_step_content(5)
    if step5_content:
        pdf.chapter_title("Step 5: Character Synopses")
        pdf.add_character_list(step5_content)

    # Step 6: Detailed Story Synopsis
    step6_content = story.get_step_content(6)
    if step6_content:
        pdf.chapter_title("Step 6: Detailed Story Synopsis")
        pdf.add_text(step6_content)

    # Step 7: Character Charts
    step7_content = story.get_step_content(7)
    if step7_content:
        pdf.chapter_title("Step 7: Character Charts")
        pdf.add_character_list(step7_content)

    # Step 8: Scene List
    step8_content = story.get_step_content(8)
    if step8_content:
        pdf.chapter_title("Step 8: Scene List")
        pdf.add_scene_list(step8_content)

    # Step 9: Scene Expansions
    step9_content = story.get_step_content(9)
    if step9_content:
        pdf.chapter_title("Step 9: Scene Expansions")
        pdf.add_scene_expansions(step9_content)

    return bytes(pdf.output(dest="S"))
