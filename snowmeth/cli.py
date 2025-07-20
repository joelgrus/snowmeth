"""CLI commands for the Snowflake Method writing assistant."""

import click

from .config import LLMConfig
from .project import ProjectManager
from .workflow import SnowflakeWorkflow, StepProgression
from .renderer import StoryRenderer
import json


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

    current_step = story.get_current_step()

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

    current_step = story.get_current_step()
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

    current_step = story.get_current_step()
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
    elif current_step == 5:
        click.echo("Expanding to detailed four-page plot synopsis...")
    elif current_step == 6:
        click.echo("Generating detailed character charts for each character...")

    # Attempt to advance
    success, message, content = progression.advance_step(story)

    if not success:
        click.echo(f"Error: {message}")
        return

    # Handle special case for Step 7 (individual character charts)
    if current_step == 6 and next_step == 7 and content == "INDIVIDUAL_CHARACTERS":
        _handle_step_7_character_charts(story, workflow, renderer)
        return

    # Handle special case for Step 9 (individual scene expansions)
    if current_step == 8 and next_step == 9 and content == "INDIVIDUAL_SCENES":
        _handle_step_9_scene_expansions(story, workflow, renderer)
        return

    # Show generated content
    click.echo(renderer.format_generated_content(content, next_step, f"\n{message}"))

    # Ask user to accept or reject
    step_names = {
        2: "paragraph expansion",
        3: "character summaries",
        4: "plot summary",
        5: "character synopses",
        6: "detailed plot synopsis",
        8: "scene breakdown",
    }
    step_name = step_names.get(next_step, f"step {next_step} content")

    if click.confirm(f"\nAccept this {step_name}?", default=True):
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


def _handle_step_7_character_charts(story, workflow, renderer):
    """Handle Step 7 individual character chart generation"""
    try:
        # Get character names from Step 3
        character_names = workflow.get_character_names(story)
        click.echo(f"Found {len(character_names)} characters to expand:")
        for name in character_names:
            click.echo(f"  • {name}")

        character_charts = {}
        accept_all = False

        # Ask user about bulk acceptance for multiple characters
        if len(character_names) > 2:  # Only offer bulk option for 3+ characters
            click.echo(f"\nYou have {len(character_names)} characters to expand.")
            bulk_choice = click.prompt(
                "Choose an option:\n  1. Review each character individually\n  2. Accept all characters automatically\n  3. Cancel\nChoice",
                type=click.Choice(['1', '2', '3']),
                default='1'
            )
            
            if bulk_choice == '2':
                accept_all = True
                click.echo("Will accept all character charts automatically...")
            elif bulk_choice == '3':
                click.echo("Character chart generation cancelled.")
                return

        # Generate chart for each character individually
        for i, character_name in enumerate(character_names, 1):
            click.echo(
                f"\n[{i}/{len(character_names)}] Generating detailed chart for {character_name}..."
            )

            try:
                chart = workflow.generate_detailed_character_chart(
                    story, character_name
                )

                # Show the generated chart
                click.echo(f"\nGenerated character chart for {character_name}:")
                click.echo(chart)

                # Ask user to accept or reject this character (or auto-accept if accept_all is True)
                if accept_all or click.confirm(
                    f"\nAccept this character chart for {character_name}?", default=True
                ):
                    character_charts[character_name] = chart
                    click.echo(f"✓ Character chart for {character_name} accepted.")
                else:
                    click.echo(f"✗ Character chart for {character_name} rejected.")
                    # Ask if they want to regenerate
                    if click.confirm(
                        f"Regenerate character chart for {character_name}?", default=False
                    ):
                        # Regenerate the character
                        click.echo(f"Regenerating chart for {character_name}...")
                        chart = workflow.generate_detailed_character_chart(
                            story, character_name
                        )
                        click.echo(
                            f"\nRegenerated character chart for {character_name}:"
                        )
                        click.echo(chart)

                        if click.confirm(
                            f"\nAccept this regenerated chart for {character_name}?", default=True
                        ):
                            character_charts[character_name] = chart
                            click.echo(
                                f"✓ Regenerated character chart for {character_name} accepted."
                            )
                        else:
                            click.echo(
                                f"✗ Skipping {character_name} - no character chart saved."
                            )
                    else:
                        click.echo(
                            f"✗ Skipping {character_name} - no character chart saved."
                        )

            except Exception as e:
                click.echo(f"Error generating chart for {character_name}: {e}")
                continue

        # Save all accepted character charts
        if character_charts:
            # Convert to JSON format like other character steps
            charts_json = json.dumps(character_charts, indent=2)
            story.set_step_content(7, charts_json)
            story.save()
            click.echo(
                f"\n✓ Character charts saved as Step 7 ({len(character_charts)} characters)."
            )
        else:
            click.echo("\n✗ No character charts were accepted. Staying on Step 6.")

    except Exception as e:
        click.echo(f"Error in Step 7 generation: {e}")


def _handle_step_9_scene_expansions(story, workflow, renderer):
    """Handle Step 9 individual scene expansion generation"""
    try:
        # Get scene list from Step 8
        scene_list = workflow.get_scene_list(story)
        click.echo(f"Found {len(scene_list)} scenes to expand:")
        for scene in scene_list:
            scene_num = scene.get("scene_number", "?")
            pov = scene.get("pov_character", "Unknown")
            desc = scene.get("scene_description", "No description")[:50]
            click.echo(f"  • Scene {scene_num}: {desc}... (POV: {pov})")

        scene_expansions = {}
        accept_all = False

        # Ask user about bulk acceptance
        if len(scene_list) > 5:  # Only offer bulk option for larger sets
            click.echo(f"\nYou have {len(scene_list)} scenes to expand. This will take some time.")
            bulk_choice = click.prompt(
                "Choose an option:\n  1. Review each scene individually\n  2. Accept all scenes automatically\n  3. Cancel\nChoice",
                type=click.Choice(['1', '2', '3']),
                default='1'
            )
            
            if bulk_choice == '2':
                accept_all = True
                click.echo("Will accept all scene expansions automatically...")
            elif bulk_choice == '3':
                click.echo("Scene expansion cancelled.")
                return

        # Generate expansion for each scene individually
        for i, scene in enumerate(scene_list, 1):
            scene_num = scene.get("scene_number", i)
            pov = scene.get("pov_character", "Unknown")
            
            click.echo(
                f"\n[{i}/{len(scene_list)}] Expanding Scene {scene_num} (POV: {pov})..."
            )

            try:
                expansion = workflow.expand_scene(story, scene_num)

                # Parse the expansion to show it nicely
                try:
                    expansion_data = json.loads(expansion)
                    title = expansion_data.get("title", f"Scene {scene_num}")
                    click.echo(f"\nGenerated expansion for Scene {scene_num}: {title}")
                    
                    # Show a rich preview
                    setting = expansion_data.get("setting", "")
                    scene_goal = expansion_data.get("scene_goal", "")
                    char_goal = expansion_data.get("character_goal", "")
                    key_beats = expansion_data.get("key_beats", [])
                    emotional_arc = expansion_data.get("emotional_arc", "")
                    
                    if setting:
                        click.echo(f"  Setting: {setting[:100]}{'...' if len(setting) > 100 else ''}")
                    if scene_goal:
                        click.echo(f"  Scene Goal: {scene_goal}")
                    if char_goal:
                        click.echo(f"  Character Goal: {char_goal}")
                    if key_beats:
                        click.echo(f"  Key Beats ({len(key_beats)} total):")
                        for i, beat in enumerate(key_beats[:3], 1):  # Show first 3 beats
                            click.echo(f"    {i}. {beat[:80]}{'...' if len(beat) > 80 else ''}")
                        if len(key_beats) > 3:
                            click.echo(f"    ... and {len(key_beats) - 3} more beats")
                    if emotional_arc:
                        click.echo(f"  Emotional Arc: {emotional_arc[:100]}{'...' if len(emotional_arc) > 100 else ''}")
                        
                except Exception as parse_error:
                    click.echo(f"\nGenerated expansion for Scene {scene_num}:")
                    click.echo(expansion[:200] + "..." if len(expansion) > 200 else expansion)
                    click.echo(f"  (JSON parse error: {parse_error})")

                # Ask user to accept or reject this scene (or auto-accept if accept_all is True)
                if accept_all or click.confirm(
                    f"\nAccept this scene expansion for Scene {scene_num}?", default=True
                ):
                    try:
                        scene_expansions[f"scene_{scene_num}"] = json.loads(expansion)
                    except:
                        scene_expansions[f"scene_{scene_num}"] = expansion
                    click.echo(f"✓ Scene expansion for Scene {scene_num} accepted.")
                else:
                    click.echo(f"✗ Scene expansion for Scene {scene_num} rejected.")
                    # Ask if they want to regenerate
                    if click.confirm(
                        f"Regenerate scene expansion for Scene {scene_num}?", default=False
                    ):
                        # Regenerate the scene
                        click.echo(f"Regenerating expansion for Scene {scene_num}...")
                        expansion = workflow.expand_scene(story, scene_num)
                        
                        try:
                            expansion_data = json.loads(expansion)
                            title = expansion_data.get("title", f"Scene {scene_num}")
                            click.echo(f"\nRegenerated expansion for Scene {scene_num}: {title}")
                        except:
                            click.echo(f"\nRegenerated expansion for Scene {scene_num}:")
                            click.echo(expansion[:200] + "..." if len(expansion) > 200 else expansion)

                        if click.confirm(
                            f"\nAccept this regenerated expansion for Scene {scene_num}?", default=True
                        ):
                            try:
                                scene_expansions[f"scene_{scene_num}"] = json.loads(expansion)
                            except:
                                scene_expansions[f"scene_{scene_num}"] = expansion
                            click.echo(
                                f"✓ Regenerated scene expansion for Scene {scene_num} accepted."
                            )
                        else:
                            click.echo(
                                f"✗ Skipping Scene {scene_num} - no scene expansion saved."
                            )
                    else:
                        click.echo(
                            f"✗ Skipping Scene {scene_num} - no scene expansion saved."
                        )

            except Exception as e:
                click.echo(f"Error generating expansion for Scene {scene_num}: {e}")
                continue

        # Save all accepted scene expansions
        if scene_expansions:
            # Convert to JSON format
            expansions_json = json.dumps(scene_expansions, indent=2)
            story.set_step_content(9, expansions_json)
            story.save()
            click.echo(
                f"\n✓ Scene expansions saved as Step 9 ({len(scene_expansions)} scenes)."
            )
        else:
            click.echo("\n✗ No scene expansions were accepted. Staying on Step 8.")

    except Exception as e:
        click.echo(f"Error in Step 9 generation: {e}")


if __name__ == "__main__":
    cli()
