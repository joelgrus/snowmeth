"""CLI commands for the Snowflake Method writing assistant."""

import json

import click

from .agents import SnowflakeAgent
from .project import ProjectManager


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
        click.echo(
            "No stories found. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
        return

    click.echo("Stories:")
    for story in stories:
        marker = "→" if story["current"] else " "
        click.echo(f"  {marker} {story['slug']}: {story['story_idea']}")


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
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
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

    # Show Step 3 if available
    characters = story.get_step_content(3)
    if characters:
        click.echo("\nStep 3 - Character summaries:")
        try:
            char_dict = json.loads(characters)
            for i, (name, summary) in enumerate(char_dict.items()):
                if i > 0:
                    click.echo()  # Add blank line between characters
                click.echo(f"  • {name}:")
                # Indent the character summary for better readability
                for line in summary.split("\n"):
                    click.echo(f"    {line}")
        except (json.JSONDecodeError, AttributeError):
            # Fallback if not valid JSON
            click.echo(f"{characters}")

    # Show Step 4 if available
    plot = story.get_step_content(4)
    if plot:
        click.echo("\nStep 4 - Plot summary:")
        click.echo(f"{plot}")

    # Show next step hint
    if story.data["current_step"] == 1 and sentence:
        click.echo(
            "\n💡 Ready for next step? Use 'snowmeth next' to expand to paragraph."
        )
    elif story.data["current_step"] == 2 and paragraph:
        click.echo(
            "\n💡 Ready for next step? Use 'snowmeth next' to extract characters."
        )
    elif story.data["current_step"] == 3 and characters:
        click.echo("\n💡 Ready for next step? Use 'snowmeth next' to expand plot.")
    elif story.data["current_step"] == 4 and plot:
        click.echo("\n💡 Step 5 (character expansion) coming soon!")


@cli.command()
def show():
    """Show current project state (alias for current)"""
    current()


@cli.command()
@click.argument("instructions")
def refine(instructions: str):
    """Refine the current step using AI with specific instructions"""
    manager = ProjectManager()
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
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
    refined = agent.refine_content(
        current_content, content_type, story_context, instructions
    )

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
        click.echo(
            f"✗ Refinement rejected. Original step {current_step} content unchanged."
        )


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
    story = manager.get_current_story()

    if not story:
        click.echo(
            "No current story. Use 'snowmeth new <slug> <story_idea>' to create one."
        )
        return

    current_step = story.data["current_step"]
    next_step = current_step + 1

    # Check if we can advance
    if not story.can_advance_to_step(next_step):
        click.echo(
            f"Cannot advance to step {next_step}. Complete step {current_step} first."
        )
        return

    # Handle different step progressions
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

    elif current_step == 2 and next_step == 3:
        # Extract characters from story context
        click.echo("Extracting main characters from story...")

        # Build story context for character extraction
        story_context = story.get_story_context(up_to_step=2)

        agent = SnowflakeAgent()
        characters_json = agent.extract_characters(story_context)

        click.echo("\nGenerated character summaries:")
        click.echo(f"{characters_json}")

        if click.confirm("\nAccept these character summaries?"):
            story.set_step_content(3, characters_json)
            story.save()
            click.echo("✓ Character summaries accepted and saved as Step 3.")
        else:
            click.echo("✗ Character summaries rejected. Staying on Step 2.")

    elif current_step == 3 and next_step == 4:
        # Expand to detailed plot summary
        click.echo("Expanding story into detailed one-page plot summary...")

        # Build full story context including characters
        story_context = story.get_story_context(up_to_step=3)

        agent = SnowflakeAgent()
        plot_summary = agent.expand_to_plot(story_context)

        click.echo("\nGenerated plot summary:")
        click.echo(f"{plot_summary}")

        if click.confirm("\nAccept this plot summary?"):
            story.set_step_content(4, plot_summary)
            story.save()
            click.echo("✓ Plot summary accepted and saved as Step 4.")
        else:
            click.echo("✗ Plot summary rejected. Staying on Step 3.")

    else:
        click.echo(f"Step {current_step} -> {next_step} expansion not yet implemented.")


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
    import os

    click.echo("Snowmeth System Status:")
    click.echo("=" * 25)

    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        # Show only first/last few chars for security
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        click.echo(f"✓ OpenAI API Key: {masked_key}")
    else:
        click.echo("✗ OpenAI API Key: Not set")
        click.echo("  Set with: export OPENAI_API_KEY=your_api_key_here")

    # Check project structure
    manager = ProjectManager()
    stories = manager.list_stories()
    click.echo(f"✓ Stories found: {len(stories)}")

    if stories:
        current_story = manager.get_current_story()
        if current_story:
            click.echo(f"✓ Current story: {current_story.data['slug']}")
        else:
            click.echo("✗ No current story selected")

    click.echo(
        "\nReady to use snowmeth!"
        if api_key
        else "\nSet OPENAI_API_KEY to use AI features."
    )


if __name__ == "__main__":
    cli()
