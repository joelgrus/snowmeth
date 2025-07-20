"""CLI commands for the Snowflake Method writing assistant."""

import click

from .config import LLMConfig
from .project import ProjectManager
from .workflow import SnowflakeWorkflow, StepProgression, AnalysisWorkflow
from .renderer import StoryRenderer
from .exceptions import (
    SnowmethError
)
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

    except SnowmethError as e:
        click.echo(f"Error: {e}")


@cli.command()
def list():
    """List all stories"""
    manager = ProjectManager()
    renderer = StoryRenderer()
    stories = manager.list_stories()
    
    # Get current story identifier for highlighting
    current_story_id = manager.context.get_current_story_identifier()

    click.echo(renderer.format_story_list(stories, current_story_id))


@cli.command()
@click.argument("slug")
def switch(slug: str):
    """Switch to a different story"""
    manager = ProjectManager()

    try:
        manager.switch_story(slug)
        click.echo(f"✓ Switched to story: '{slug}'")
    except SnowmethError as e:
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
    except SnowmethError as e:
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
        9.5: "story analysis",
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
    except SnowmethError as e:
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
    # Generate all character charts using business logic
    success, character_charts, errors = workflow.handle_character_charts_generation(story)
    
    if not success:
        click.echo("Error generating character charts:")
        for error in errors:
            click.echo(f"  • {error}")
        return
    
    # Show errors if any
    if errors:
        click.echo("Some errors occurred:")
        for error in errors:
            click.echo(f"  ⚠️  {error}")
    
    character_names = list(character_charts.keys())
    click.echo(f"Found {len(character_names)} characters to expand:")
    for name in character_names:
        click.echo(f"  • {name}")

    accepted_charts = {}
    accept_all = False

    # Ask user about bulk acceptance for multiple characters
    if len(character_names) > 2:
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

    # Review each character chart
    for i, (character_name, chart) in enumerate(character_charts.items(), 1):
        click.echo(f"\n[{i}/{len(character_names)}] Character chart for {character_name}:")
        click.echo(chart)

        # Ask user to accept or reject this character (or auto-accept if accept_all is True)
        if accept_all or click.confirm(f"\nAccept this character chart for {character_name}?", default=True):
            accepted_charts[character_name] = chart
            click.echo(f"✓ Character chart for {character_name} accepted.")
        else:
            click.echo(f"✗ Character chart for {character_name} rejected.")

    # Save all accepted character charts
    if accepted_charts:
        charts_json = json.dumps(accepted_charts, indent=2)
        story.set_step_content(7, charts_json)
        story.save()
        click.echo(f"\n✓ Character charts saved as Step 7 ({len(accepted_charts)} characters).")
    else:
        click.echo("\n✗ No character charts were accepted. Staying on Step 6.")


def _handle_step_9_scene_expansions(story, workflow, renderer):
    """Handle Step 9 individual scene expansion generation"""
    # Generate all scene expansions using business logic
    success, scene_expansions, errors = workflow.handle_scene_expansions_generation(story)
    
    if not success:
        click.echo("Error generating scene expansions:")
        for error in errors:
            click.echo(f"  • {error}")
        return
    
    # Show errors if any
    if errors:
        click.echo("Some errors occurred:")
        for error in errors:
            click.echo(f"  ⚠️  {error}")
    
    # Show scene summary
    scene_count = len(scene_expansions)
    click.echo(f"Found {scene_count} scenes to expand:")
    for scene_key in scene_expansions.keys():
        scene_num = scene_key.replace("scene_", "")
        click.echo(f"  • Scene {scene_num}")

    accepted_expansions = {}
    accept_all = False

    # Ask user about bulk acceptance
    if scene_count > 5:
        click.echo(f"\nYou have {scene_count} scenes to expand. This will take some time.")
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

    # Review each scene expansion
    for i, (scene_key, expansion_data) in enumerate(scene_expansions.items(), 1):
        scene_num = scene_key.replace("scene_", "")
        
        # Display expansion preview
        if isinstance(expansion_data, dict):
            title = expansion_data.get("title", f"Scene {scene_num}")
            click.echo(f"\n[{i}/{scene_count}] Scene {scene_num}: {title}")
            
            # Show preview details
            setting = expansion_data.get("setting", "")
            if setting:
                click.echo(f"  Setting: {setting[:100]}{'...' if len(setting) > 100 else ''}")
            
            key_beats = expansion_data.get("key_beats", [])
            if key_beats:
                click.echo(f"  Key Beats ({len(key_beats)} total)")
        else:
            click.echo(f"\n[{i}/{scene_count}] Scene {scene_num}:")
            click.echo(f"  {str(expansion_data)[:200]}{'...' if len(str(expansion_data)) > 200 else ''}")

        # Ask user to accept or reject this scene (or auto-accept if accept_all is True)
        if accept_all or click.confirm(f"\nAccept this scene expansion for Scene {scene_num}?", default=True):
            accepted_expansions[scene_key] = expansion_data
            click.echo(f"✓ Scene expansion for Scene {scene_num} accepted.")
        else:
            click.echo(f"✗ Scene expansion for Scene {scene_num} rejected.")

    # Save all accepted scene expansions
    if accepted_expansions:
        expansions_json = json.dumps(accepted_expansions, indent=2)
        story.set_step_content(9, expansions_json)
        story.save()
        click.echo(f"\n✓ Scene expansions saved as Step 9 ({len(accepted_expansions)} scenes).")
    else:
        click.echo("\n✗ No scene expansions were accepted. Staying on Step 8.")


@cli.command()
def analyze():
    """Analyze story for consistency and completeness"""
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    story = manager.get_current_story()

    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return

    if story.get_current_step() < 10:
        click.echo("Story must be at Step 10 (completed Snowflake Method) to analyze.")
        click.echo(f"Current step: {story.get_current_step()}")
        return

    try:
        click.echo("🔍 Analyzing your story for consistency and completeness...")
        
        # Generate analysis
        try:
            analysis_workflow = AnalysisWorkflow(workflow)
            analysis = analysis_workflow.analyze_story(story)
            click.echo(f"DEBUG: Analysis type: {type(analysis)}")
            click.echo(f"DEBUG: Analysis preview: {str(analysis)[:200]}...")
        except Exception as e:
            click.echo(f"❌ Error during story analysis: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Save analysis to separate file
        analysis_file = manager.stories_dir / f"{story.data['slug']}-analysis.json"
        with open(analysis_file, 'w') as f:
            f.write(analysis)
        
        # Parse and display results
        try:
            analysis_data = json.loads(analysis)
            
            # Debug: Show what we got after first parse
            click.echo(f"DEBUG: First parse result type: {type(analysis_data)}")
            if isinstance(analysis_data, str):
                click.echo(f"DEBUG: String content preview: {analysis_data[:200]}...")
            
            # Handle case where model returns a JSON-encoded string
            if isinstance(analysis_data, str):
                try:
                    analysis_data = json.loads(analysis_data)
                    click.echo(f"DEBUG: Second parse result type: {type(analysis_data)}")
                except json.JSONDecodeError as e:
                    click.echo(f"DEBUG: Second parse failed: {e}")
                    pass  # Keep as string if second parse fails
                    
        except json.JSONDecodeError as e:
            click.echo(f"❌ Error parsing analysis results: {e}")
            click.echo(f"Raw analysis saved to: {analysis_file}")
            click.echo("Raw response:")
            click.echo(analysis)
            return
        
        if not isinstance(analysis_data, dict):
            click.echo(f"❌ Expected analysis to be a JSON object, got: {type(analysis_data)}")
            click.echo(f"Raw analysis saved to: {analysis_file}")
            click.echo("Raw response:")
            click.echo(analysis)
            return
        
        # Show results
        click.echo("\n📊 Story Analysis Results:")
        
        overall = analysis_data.get("overall_assessment", {})
        readiness_score = overall.get("readiness_score", "N/A")
        click.echo(f"📈 Readiness Score: {readiness_score}")
        
        strengths = overall.get("key_strengths", [])
        if strengths:
            click.echo("\n✅ Key Strengths:")
            for strength in strengths:
                click.echo(f"  • {strength}")
        
        recommendations = analysis_data.get("recommendations", {})
        high_priority = recommendations.get("high_priority", [])
        medium_priority = recommendations.get("medium_priority", [])
        
        if high_priority:
            click.echo("\n🔴 High Priority Issues:")
            for issue in high_priority:
                click.echo(f"  • {issue}")
        
        if medium_priority:
            click.echo("\n🟡 Medium Priority Issues:")
            for issue in medium_priority:
                click.echo(f"  • {issue}")
        
        # Show scene-specific recommendations
        scene_improvements = recommendations.get("scene_improvements", [])
        if scene_improvements:
            click.echo("\n🎯 Scene-Specific Improvements:")
            for improvement in scene_improvements:
                scene_num = improvement.get("scene_number", "?")
                priority = improvement.get("priority", "medium")
                issue = improvement.get("issue", "No issue specified")
                priority_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                click.echo(f"  {priority_icon} Scene {scene_num}: {issue}")
        
        total_issues = len(high_priority) + len(medium_priority)
        scene_count = len(scene_improvements)
        if total_issues > 0 or scene_count > 0:
            click.echo(f"\n💡 Found {total_issues} general issues and {scene_count} scene-specific improvements.")
            if scene_count > 0:
                scene_numbers = [str(s.get("scene_number", "?")) for s in scene_improvements]
                click.echo(f"  • Run 'snowmeth improve-all' to fix scenes: {', '.join(scene_numbers)}")
            else:
                click.echo("  • Run 'snowmeth improve-all' to fix all issues automatically")
            click.echo("  • Run 'snowmeth improve scene N' to fix specific scenes")
            click.echo("  • Run 'snowmeth revision-status' for a quick summary")
        else:
            click.echo("\n🎉 Your story looks great! No major issues found.")
            
    except Exception as e:
        click.echo(f"Error during analysis: {e}")


@cli.command()
def revision_status():
    """Show quick revision status from latest analysis"""
    manager = ProjectManager()
    story = manager.get_current_story()

    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return

    # Check if we have analysis
    analysis_file = manager.stories_dir / f"{story.data['slug']}-analysis.json"
    if not analysis_file.exists():
        click.echo("No analysis found. Run 'snowmeth analyze' first.")
        return
    
    try:
        # Load analysis
        with open(analysis_file, 'r') as f:
            analysis_data = json.loads(f.read())
        
        # Show quick summary
        overall = analysis_data.get("overall_assessment", {})
        readiness_score = overall.get("readiness_score", "N/A")
        
        recommendations = analysis_data.get("recommendations", {})
        high_priority = recommendations.get("high_priority", [])
        medium_priority = recommendations.get("medium_priority", [])
        
        click.echo("📊 Story Status:")
        click.echo(f"📈 Readiness Score: {readiness_score}")
        click.echo(f"🔴 High Priority Issues: {len(high_priority)}")
        click.echo(f"🟡 Medium Priority Issues: {len(medium_priority)}")
        
        if high_priority or medium_priority:
            click.echo("\n💡 Next steps:")
            click.echo("  • Run 'snowmeth improve-all' to fix all issues")
            click.echo("  • Run 'snowmeth analyze' for detailed analysis")
        else:
            click.echo("\n🎉 Your story is ready!")
            
    except Exception as e:
        click.echo(f"Error reading analysis: {e}")


def _get_change_summary(old_scene, new_scene):
    """Generate a summary of changes between old and new scene data"""
    old_title = old_scene.get('title', 'Untitled')
    new_title = new_scene.get('title', 'Untitled')
    
    # Check title changes
    if 'Placeholder' in old_title and 'Placeholder' not in new_title:
        return f"Expanded from placeholder to '{new_title}'"
    elif old_title != new_title:
        # Check if title change was necessary
        if 'Placeholder' in old_title or ('Scene ' in old_title and old_title.count(' ') <= 2):
            return f"Improved title: '{old_title}' → '{new_title}'"
        else:
            return f"⚠️  Title changed unnecessarily: '{old_title}' → '{new_title}'"
    else:
        # Check for content improvements
        old_beats = len(old_scene.get('key_beats', []))
        new_beats = len(new_scene.get('key_beats', []))
        old_motivation_len = len(old_scene.get('character_motivation', ''))
        new_motivation_len = len(new_scene.get('character_motivation', ''))
        old_goal_len = len(old_scene.get('scene_goal', ''))
        new_goal_len = len(new_scene.get('scene_goal', ''))
        
        changes = []
        if new_beats > old_beats:
            changes.append(f"{new_beats - old_beats} more story beats")
        if new_motivation_len > old_motivation_len + 50:
            changes.append("enhanced character motivation")
        if new_goal_len > old_goal_len + 30:
            changes.append("improved scene goal")
        
        if changes:
            return f"Enhanced content: {', '.join(changes)}"
        else:
            return "Refined content and structure"


@cli.command()
@click.option("--auto", is_flag=True, help="Skip confirmation prompts")
def improve_all(auto):
    """Improve all scenes flagged in the latest analysis"""
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    analysis_workflow = AnalysisWorkflow(workflow)
    story = manager.get_current_story()

    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return

    # Check if we have analysis
    analysis_file = manager.stories_dir / f"{story.data['slug']}-analysis.json"
    if not analysis_file.exists():
        click.echo("No analysis found. Run 'snowmeth analyze' first.")
        return
    
    try:
        # Load analysis
        with open(analysis_file, 'r') as f:
            analysis_data = json.loads(f.read())
        
        # Check if there are issues to address
        recommendations = analysis_data.get("recommendations", {})
        high_priority = recommendations.get("high_priority", [])
        medium_priority = recommendations.get("medium_priority", [])
        
        if not high_priority and not medium_priority:
            click.echo("🎉 No issues found in analysis! Your story looks good.")
            return
        
        # Identify scenes that need improvement using business logic
        scenes_to_improve = analysis_workflow.identify_scenes_needing_improvement(story, analysis_data)
        
        # If no specific scenes found, ask the user
        if not scenes_to_improve:
            click.echo("No specific scenes identified from analysis issues.")
            scene_input = click.prompt(
                "Which scenes would you like to improve? (e.g., '1,3,5' or 'all' for all scenes)",
                default="",
                show_default=False
            )
            
            if not scene_input:
                click.echo("No scenes specified. Improvement cancelled.")
                return
            elif scene_input.lower() == 'all':
                # Get all scene numbers from Step 9
                step9_content = story.get_step_content(9)
                if step9_content:
                    current_expansions = json.loads(step9_content)
                    scenes_to_improve = [int(key.split('_')[1]) for key in current_expansions.keys() if key.startswith('scene_')]
                else:
                    click.echo("No Step 9 content found.")
                    return
            else:
                try:
                    scenes_to_improve = [int(x.strip()) for x in scene_input.split(',')]
                except ValueError:
                    click.echo("Error: Please enter scene numbers as integers (e.g., '1,3,5')")
                    return
        
        total_issues = len(high_priority) + len(medium_priority)
        click.echo(f"🔄 Found {total_issues} issues to address.")
        click.echo(f"📝 Will improve {len(scenes_to_improve)} scenes: {', '.join(map(str, scenes_to_improve))}")
        
        if not auto and not click.confirm("Proceed with improvements?", default=True):
            click.echo("Improvement cancelled.")
            return
        
        # Improve scenes using business logic
        improved_count, errors = analysis_workflow.improve_scenes(story, scenes_to_improve, analysis_data)
        
        # Show results
        if errors:
            click.echo("Some errors occurred:")
            for error in errors:
                click.echo(f"  ⚠️  {error}")
        
        if improved_count > 0:
            click.echo(f"\n🎉 Improved {improved_count} scenes!")
            click.echo("💡 Run 'snowmeth analyze' to see updated analysis.")
        else:
            click.echo("\n❌ No scenes were improved.")
        
    except Exception as e:
        click.echo(f"Error during improvement: {e}")


@cli.command()
@click.argument("scene_numbers")
def improve(scene_numbers):
    """Improve specific scenes (e.g., 'snowmeth improve 3' or 'snowmeth improve 1,5,7')"""
    manager = ProjectManager()
    workflow = SnowflakeWorkflow()
    story = manager.get_current_story()

    if not story:
        click.echo("No current story. Use 'snowmeth new <slug> <story_idea>' to create one.")
        return

    if story.get_current_step() < 9:
        click.echo("Story must be at Step 9 or higher to improve scenes.")
        click.echo(f"Current step: {story.get_current_step()}")
        return

    try:
        # Parse scene numbers
        if ',' in scene_numbers:
            scene_nums = [int(x.strip()) for x in scene_numbers.split(',')]
        else:
            scene_nums = [int(scene_numbers)]
        
        # Get current scene expansions
        step9_content = story.get_step_content(9)
        if not step9_content:
            click.echo("No Step 9 content found. Run 'snowmeth next' to generate scene expansions first.")
            return
            
        current_expansions = json.loads(step9_content)
        
        # Improve each requested scene
        improved_count = 0
        for scene_num in scene_nums:
            try:
                click.echo(f"\n🔄 Improving Scene {scene_num}...")
                
                scene_key = f"scene_{scene_num}"
                if scene_key not in current_expansions:
                    click.echo(f"⚠️  Scene {scene_num} not found, skipping.")
                    continue
                
                # For manual improvements, use general enhancement guidance
                improvement_guidance = "Enhance character development, emotional depth, concrete story details, and address any plot inconsistencies or pacing issues"
                
                # Use targeted improvement
                improved_scene = workflow.improve_scene(story, scene_num, improvement_guidance)
                
                # Parse and update
                try:
                    improved_scene_data = json.loads(improved_scene)
                    
                    # Show what changed
                    old_title = current_expansions[scene_key].get('title', 'Untitled')
                    new_title = improved_scene_data.get('title', 'Untitled')
                    
                    # Brief summary of changes
                    if 'Placeholder' in old_title and 'Placeholder' not in new_title:
                        change_summary = f"Expanded from placeholder to '{new_title}'"
                    elif old_title != new_title:
                        change_summary = f"Updated title: '{old_title}' → '{new_title}'"
                    else:
                        # Check for other significant changes
                        old_beats = len(current_expansions[scene_key].get('key_beats', []))
                        new_beats = len(improved_scene_data.get('key_beats', []))
                        if new_beats > old_beats:
                            change_summary = f"Enhanced with {new_beats - old_beats} additional story beats"
                        else:
                            change_summary = "Refined content and structure"
                    
                    current_expansions[scene_key] = improved_scene_data
                    
                    # Save updated scenes
                    story.set_step_content(9, json.dumps(current_expansions, indent=2))
                    story.save()
                    
                    improved_count += 1
                    click.echo(f"✅ Scene {scene_num} improved: {change_summary}")
                    
                except json.JSONDecodeError as e:
                    click.echo(f"⚠️  Could not parse improved Scene {scene_num}: {e}")
                    
            except Exception as e:
                click.echo(f"❌ Error improving Scene {scene_num}: {e}")
        
        click.echo(f"\n🎉 Improved {improved_count} scenes!")
        click.echo("💡 Run 'snowmeth analyze' to see updated analysis.")
        
    except ValueError:
        click.echo("Error: Scene numbers must be integers (e.g., '3' or '1,5,7')")
    except Exception as e:
        click.echo(f"Error during improvement: {e}")


if __name__ == "__main__":
    cli()
