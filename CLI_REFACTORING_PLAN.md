# CLI Refactoring Plan

## Current Issue
- `snowmeth/cli.py` is 912 lines long - too large for maintainability
- Mixed concerns: commands, handlers, and utility functions all in one file

## Proposed Structure

```
snowmeth/
├── cli/
│   ├── __init__.py          # Main CLI group and imports
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── basic.py         # new, list, switch, current, show, delete
│   │   ├── content.py       # refine, edit, next  
│   │   ├── system.py        # status, set_model, models
│   │   └── analysis.py      # analyze, revision_status, improve_all, improve
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── step_handlers.py # _handle_step_7_character_charts, _handle_step_9_scene_expansions
│   │   └── improvement.py   # _get_change_summary and improvement logic
│   └── formatters/
│       ├── __init__.py
│       └── output.py        # Move from renderer.py if needed
```

## Migration Steps

1. **Create CLI package structure**
   ```bash
   mkdir -p snowmeth/cli/commands snowmeth/cli/handlers snowmeth/cli/formatters
   ```

2. **Split commands by concern**:
   - `basic.py`: new, list, switch, current, show, delete (~150 lines)
   - `content.py`: refine, edit, next (~200 lines)  
   - `system.py`: status, set_model, models (~50 lines)
   - `analysis.py`: analyze, revision_status, improve_all, improve (~400 lines)

3. **Extract handlers**:
   - Move `_handle_step_7_character_charts` and `_handle_step_9_scene_expansions` to `handlers/step_handlers.py`
   - Move `_get_change_summary` to `handlers/improvement.py`

4. **Update main CLI**:
   - `cli/__init__.py` imports all command groups and registers them
   - Update `pyproject.toml` entry point to point to `snowmeth.cli:cli`

## Benefits
- Each file under 200 lines
- Clear separation of concerns  
- Easier testing and maintenance
- Better code organization

## Estimated Effort
- 2-3 hours for complete refactoring
- Low risk - mostly moving code around
- Can be done incrementally