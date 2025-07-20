import json
import re
from pathlib import Path
from typing import Optional, List

import click
import dspy


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
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {"current_story": None}
    
    def _save_config(self):
        """Save global config"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _sanitize_slug(self, slug: str) -> str:
        """Convert slug to safe filename"""
        # Replace spaces and special chars with hyphens, lowercase
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '-', slug.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')
    
    def create_story(self, slug: str, story_idea: str) -> 'Story':
        """Create a new story"""
        clean_slug = self._sanitize_slug(slug)
        story_file = self.stories_dir / f"{clean_slug}.json"
        
        if story_file.exists():
            raise click.ClickException(f"Story '{clean_slug}' already exists")
        
        story_data = {
            "slug": clean_slug,
            "story_idea": story_idea,
            "current_step": 1,
            "steps": {}
        }
        
        with open(story_file, 'w') as f:
            json.dump(story_data, f, indent=2)
        
        # Set as current story
        self.config["current_story"] = clean_slug
        self._save_config()
        
        return Story(story_file)
    
    def get_current_story(self) -> Optional['Story']:
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
                with open(story_file, 'r') as f:
                    data = json.load(f)
                stories.append({
                    "slug": data["slug"],
                    "story_idea": data["story_idea"],
                    "current": data["slug"] == self.config["current_story"]
                })
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
        with open(self.story_file, 'r') as f:
            return json.load(f)
    
    def save(self):
        """Save story data to JSON file"""
        with open(self.story_file, 'w') as f:
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
        
        # Update current step if we're progressing forward
        if step > self.data["current_step"]:
            self.data["current_step"] = step
    
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
            up_to_step = self.data["current_step"]
        
        context_parts = [f"Original story idea: {self.data['story_idea']}"]
        
        # Add completed steps up to the specified step
        for step_num in range(1, up_to_step + 1):
            content = self.get_step_content(step_num)
            if content:
                step_names = {1: "One-sentence summary", 2: "Paragraph summary", 3: "Character summaries"}
                step_name = step_names.get(step_num, f"Step {step_num}")
                context_parts.append(f"{step_name}: {content}")
        
        return "\n\n".join(context_parts)


class SentenceGenerator(dspy.Signature):
    """Generate a one-sentence summary for a novel based on a story idea"""
    
    story_idea = dspy.InputField(desc="The basic story idea or concept")
    sentence = dspy.OutputField(desc="A compelling one-sentence summary of the novel")


class ContentRefiner(dspy.Signature):
    """Refine any story content based on specific instructions"""
    
    current_content = dspy.InputField(desc="The current content to refine")
    content_type = dspy.InputField(desc="Type of content: sentence, paragraph, character, etc.")
    story_context = dspy.InputField(desc="Story context including original idea and previous steps")
    refinement_instructions = dspy.InputField(desc="Specific instructions for how to refine the content")
    refined_content = dspy.OutputField(desc="The content refined according to the instructions while maintaining consistency with the story context")


class ParagraphExpander(dspy.Signature):
    """Expand a one-sentence novel summary into a full paragraph"""
    
    sentence_summary = dspy.InputField(desc="The one-sentence summary to expand")
    story_idea = dspy.InputField(desc="The original story idea for context")
    paragraph_summary = dspy.OutputField(desc="A full paragraph (4-5 sentences) expanding on the one-sentence summary, including key plot points, conflict, and stakes")


class SnowflakeAgent:
    """DSPy agent for snowflake method operations"""
    
    def __init__(self):
        # Configure OpenAI model
        try:
            self.lm = dspy.LM('openai/gpt-4o-mini')
            dspy.configure(lm=self.lm)
            
            self.generator = dspy.ChainOfThought(SentenceGenerator)
            self.refiner = dspy.ChainOfThought(ContentRefiner)
            self.expander = dspy.ChainOfThought(ParagraphExpander)
        except Exception as e:
            raise click.ClickException(f"Failed to initialize AI model. Make sure OPENAI_API_KEY is set. Error: {e}")
    
    def generate_sentence(self, story_idea: str) -> str:
        """Generate initial one-sentence summary"""
        result = self.generator(story_idea=story_idea)
        return result.sentence
    
    def refine_content(self, current_content: str, content_type: str, story_context: str, instructions: str) -> str:
        """Refine any content with specific instructions and full story context"""
        result = self.refiner(
            current_content=current_content,
            content_type=content_type,
            story_context=story_context,
            refinement_instructions=instructions
        )
        return result.refined_content
    
    def expand_to_paragraph(self, sentence: str, story_idea: str) -> str:
        """Expand one-sentence summary to paragraph"""
        result = self.expander(
            sentence_summary=sentence,
            story_idea=story_idea
        )
        return result.paragraph_summary


@click.group()
def cli():
    """Snowflake Method writing assistant"""
    pass


@cli.command()
@click.argument('slug')
@click.argument('story_idea')
def new(slug: str, story_idea: str):
    """Create a new story project"""
    manager = ProjectManager()
    
    try:
        story = manager.create_story(slug, story_idea)
        click.echo(f"Created new story: '{story.data['slug']}'")
        click.echo(f"Story idea: {story_idea}")
        click.echo("Generating initial sentence...")
        
        # Generate initial sentence
        agent = SnowflakeAgent()
        sentence = agent.generate_sentence(story_idea)
        
        story.set_step_content(1, sentence)
        story.save()
        
        click.echo("\nGenerated one-sentence summary:")
        click.echo(f"'{sentence}'")
        click.echo(f"\n✓ Story '{story.data['slug']}' is now active.")
        
    except click.ClickException as e:
        click.echo(f"Error: {e}")


@cli.command()
def list():
    """List all stories"""
    manager = ProjectManager()
    stories = manager.list_stories()
    
    if not stories:
        click.echo("No stories found. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return
    
    click.echo("Stories:")
    for story in stories:
        marker = "→" if story["current"] else " "
        click.echo(f"  {marker} {story['slug']}: {story['story_idea']}")


@cli.command()
@click.argument('slug')
def switch(slug: str):
    """Switch to a different story"""
    manager = ProjectManager()
    
    try:
        manager.switch_story(slug)
        click.echo(f"✓ Switched to story: '{slug}'")
    except click.ClickException as e:
        click.echo(f"Error: {e}")


@cli.command()
def current():
    """Show current story info"""
    manager = ProjectManager()
    story = manager.get_current_story()
    
    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return
    
    click.echo(f"Current story: {story.data['slug']}")
    click.echo(f"Story idea: {story.data['story_idea']}")
    click.echo(f"Current step: {story.data['current_step']}")
    
    # Show Step 1
    sentence = story.get_step_content(1)
    if sentence:
        click.echo("\nStep 1 - One-sentence summary:")
        click.echo(f"'{sentence}'")
    
    # Show Step 2 if available
    paragraph = story.get_step_content(2)
    if paragraph:
        click.echo("\nStep 2 - Paragraph summary:")
        click.echo(f"{paragraph}")
    
    # Show next step hint
    if story.data['current_step'] == 1 and sentence:
        click.echo("\n💡 Ready for next step? Use 'snowmeth next' to expand to paragraph.")
    elif story.data['current_step'] == 2 and paragraph:
        click.echo("\n💡 Step 3 (character development) coming soon!")


@cli.command()
def show():
    """Show current project state (alias for current)"""
    current()


@cli.command()
@click.argument('instructions')
def refine(instructions: str):
    """Refine the current step using AI with specific instructions"""
    manager = ProjectManager()
    story = manager.get_current_story()
    
    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return
    
    current_step = story.data["current_step"]
    current_content = story.get_step_content(current_step)
    
    if not current_content:
        click.echo(f"No content found for step {current_step}.")
        return
    
    # Map step numbers to content types
    step_types = {
        1: "sentence",
        2: "paragraph", 
        3: "character",
        4: "plot",
        # Add more as we implement them
    }
    
    content_type = step_types.get(current_step, f"step-{current_step}")
    
    # Show current content with appropriate formatting
    click.echo(f"Current step {current_step} ({content_type}):")
    if current_step == 1:
        click.echo(f"  '{current_content}'")
    else:
        click.echo(f"{current_content}")
    
    click.echo(f"\nRefining with instructions: '{instructions}'")
    click.echo("Generating refinement...")
    
    # Build story context for refinement
    story_context = story.get_story_context(up_to_step=current_step)
    
    agent = SnowflakeAgent()
    refined = agent.refine_content(current_content, content_type, story_context, instructions)
    
    # Show proposed refinement with appropriate formatting
    click.echo("\nProposed refinement:")
    if current_step == 1:
        click.echo(f"  '{refined}'")
    else:
        click.echo(f"{refined}")
    
    # Ask user to accept or reject
    if click.confirm("\nAccept this refinement?"):
        story.set_step_content(current_step, refined)
        story.save()
        click.echo(f"✓ Refinement accepted and saved for step {current_step}.")
    else:
        click.echo(f"✗ Refinement rejected. Original step {current_step} content unchanged.")


@cli.command()
@click.argument('new_content')
def edit(new_content: str):
    """Manually edit the current step content"""
    manager = ProjectManager()
    story = manager.get_current_story()
    
    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return
    
    current_step = story.data["current_step"]
    story.set_step_content(current_step, new_content)
    story.save()
    
    if current_step == 1:
        click.echo(f"Updated step {current_step} sentence: '{new_content}'")
    else:
        click.echo(f"Updated step {current_step} content.")
        click.echo(f"{new_content}")


@cli.command()
def next():
    """Advance to the next step in the Snowflake Method"""
    manager = ProjectManager()
    story = manager.get_current_story()
    
    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return
    
    current_step = story.data["current_step"]
    next_step = current_step + 1
    
    # Check if we can advance
    if not story.can_advance_to_step(next_step):
        click.echo(f"Cannot advance to step {next_step}. Complete step {current_step} first.")
        return
    
    # Currently only support steps 1->2
    if current_step == 1 and next_step == 2:
        # Expand sentence to paragraph
        sentence = story.get_step_content(1)
        if not sentence:
            click.echo("No sentence found in step 1. Cannot expand to paragraph.")
            return
        
        click.echo("Expanding step 1 sentence to step 2 paragraph...")
        click.echo(f"Current sentence: '{sentence}'")
        
        agent = SnowflakeAgent()
        paragraph = agent.expand_to_paragraph(sentence, story.data["story_idea"])
        
        click.echo("\nGenerated paragraph:")
        click.echo(f"{paragraph}")
        
        if click.confirm("\nAccept this paragraph expansion?"):
            story.set_step_content(2, paragraph)
            story.save()
            click.echo("✓ Paragraph accepted and saved as Step 2.")
        else:
            click.echo("✗ Paragraph rejected. Staying on Step 1.")
    
    else:
        click.echo(f"Step {current_step} -> {next_step} expansion not yet implemented.")


@cli.command()
@click.argument('slug')
def delete(slug: str):
    """Delete a story"""
    manager = ProjectManager()
    
    try:
        if click.confirm(f"Are you sure you want to delete story '{slug}'?"):
            manager.delete_story(slug)
            click.echo(f"✓ Story '{slug}' deleted.")
        else:
            click.echo("Delete cancelled.")
    except click.ClickException as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()