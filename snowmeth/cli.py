"""CLI commands for the Snowflake Method writing assistant."""

import click

from .config import LLMConfig
from .project import ProjectManager
from .workflow import SnowflakeWorkflow, StepProgression
from .renderer import StoryRenderer


@click.group()
def cli():
    """Snowflake Method writing assistant"""
    pass


@cli.command()
@click.argument("slug")
@click.argument("story_idea")
def new(slug: str, story_idea: str):
    """Create a new story project"""
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    renderer = StoryRenderer()

    try:
        story = manager.create_story(slug, story_idea)
        click.echo(f"Created new story: '{story.data['slug']}'")
        click.echo(f"Story idea: {story_idea}")
        click.echo("Generating initial sentence...")

        # Generate initial sentence
        sentence = workflow.generate_initial_sentence(story_idea)

        story.set_step_content(1, sentence)
        story.save()

        click.echo(
            renderer.format_generated_content(
                sentence, 1, "Generated one-sentence summary"
            )
        )
        click.echo(f"\n✓ Story '{story.data['slug']}' is now active.")

    except click.ClickException as e:
        click.echo(f"Error: {e}")


@cli.command()
def list():
    """List all stories"""
    manager = ProjectManager()
    renderer = StoryRenderer()
    stories = manager.list_stories()

    click.echo(renderer.format_story_list(stories))


@cli.command()
@click.argument("slug")
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
    renderer = StoryRenderer()
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
        return

    click.echo(renderer.format_story_overview(story))


@cli.command()
def show():
    """Show current project state (alias for current)"""
    current()


@cli.command()
@click.argument("instructions")
def refine(instructions: str):
    """Refine the current step using AI with specific instructions"""
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    renderer = StoryRenderer()
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
        return

    current_step = story.data["current_step"]

    try:
        # Show current content
        click.echo(renderer.format_step_content_for_editing(story, current_step))
        click.echo(f"\nRefining with instructions: '{instructions}'")
        click.echo("Generating refinement...")

        # Generate refinement
        refined = workflow.refine_content(story, instructions)

        # Show proposed refinement
        click.echo(
            renderer.format_generated_content(
                refined, current_step, "Proposed refinement"
            )
        )

        # Ask user to accept or reject
        if click.confirm("\nAccept this refinement?"):
            story.set_step_content(current_step, refined)
            story.save()
            click.echo(f"✓ Refinement accepted and saved for step {current_step}.")
        else:
            click.echo(
                f"✗ Refinement rejected. Original step {current_step} content unchanged."
            )

    except ValueError as e:
        click.echo(f"Error: {e}")
    except click.ClickException as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("new_content")
def edit(new_content: str):
    """Manually edit the current step content"""
    manager = ProjectManager()
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
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
    workflow = SnowflakeWorkflow()
    progression = StepProgression(workflow)
    renderer = StoryRenderer()
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
        return

    current_step = story.data["current_step"]
    next_step = current_step + 1

    # Show current step context
    if current_step == 1:
        sentence = story.get_step_content(1)
        click.echo("Expanding step 1 sentence to step 2 paragraph...")
        click.echo(f"Current sentence: '{sentence}'")
    elif current_step == 2:
        click.echo("Extracting main characters from story...")
    elif current_step == 3:
        click.echo("Expanding story into detailed one-page plot summary...")
    elif current_step == 4:
        click.echo("Generating character synopses from each character's POV...")

    # Attempt to advance
    success, message, content = progression.advance_step(story)

    if not success:
        click.echo(f"Error: {message}")
        return

    # Show generated content
    click.echo(renderer.format_generated_content(content, next_step, f"\n{message}"))

    # Ask user to accept or reject
    step_names = {
        2: "paragraph expansion",
        3: "character summaries",
        4: "plot summary",
        5: "character synopses",
    }
    step_name = step_names.get(next_step, f"step {next_step} content")

    if click.confirm(f"\nAccept this {step_name}?"):
        progression.accept_step_content(story, content)
        click.echo(f"✓ {step_name.title()} accepted and saved as Step {next_step}.")
    else:
        click.echo(f"✗ {step_name.title()} rejected. Staying on Step {current_step}.")


@cli.command()
@click.argument("slug")
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


@cli.command()
def status():
    """Check system status and configuration"""
    llm_config = LLMConfig()
    manager = ProjectManager()
    renderer = StoryRenderer()

    # Get status info
    default_model = llm_config.get_model("default")
    has_key, key_info = llm_config.check_api_key(default_model)
    stories = manager.list_stories()
    current_story = manager.get_current_story()
    current_story_slug = current_story.data["slug"] if current_story else None

    # Format and display
    status_text = renderer.format_system_status(
        default_model, has_key, key_info, len(stories), current_story_slug
    )
    click.echo(status_text)


@cli.command()
@click.argument("model")
def set_model(model: str):
    """Set the default model (e.g., openai/gpt-4o-mini, openrouter/google/gemini-2.5-flash-lite-preview-06-17)"""
    llm_config = LLMConfig()
    llm_config.set_model(model, "default")
    click.echo(f"✓ Default model set to: {model}")

    # Check if API key is available
    has_key, key_info = llm_config.check_api_key(model)
    if not has_key:
        api_key_env = llm_config.get_api_key_env(model)
        click.echo(f"⚠️  {key_info}")
        click.echo(f"   Set with: export {api_key_env}=your_api_key_here")


@cli.command()
def models():
    """List configured models"""
    llm_config = LLMConfig()
    renderer = StoryRenderer()
    models = llm_config.list_models()

    click.echo(renderer.format_model_list(models, llm_config))


if __name__ == "__main__":
    cli()
