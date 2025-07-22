# Agent Guidelines for snowmeth

## Task Management
- **Current tasks**: Check `TODO.md` for current project status and pending tasks
- **Update progress**: Use TodoWrite tool to track task completion during sessions
- **Prioritize work**: Focus on high-priority tasks first, especially workflow methods and step advancement

## Build/Test Commands
- **Install dependencies**: `uv sync` or `uv install`
- **Add dependencies**: `uv add <package>`
- **Run tests**: `uv run pytest`
- **Run single test**: `uv run pytest path/to/test.py::test_function`
- **Linting**: `uv run ruff check`
- **Formatting**: `uv run ruff format`

## Code Style Guidelines
- **Python version**: >=3.11 (as specified in pyproject.toml)
- **Imports**: Use standard library imports, no external dependencies currently
- **Formatting**: Follow PEP 8 conventions
- **Functions**: Use descriptive names with snake_case
- **Main pattern**: Use `if __name__ == "__main__":` guard for entry points
- **Docstrings**: Add docstrings for functions and classes
- **Type hints**: Add type annotations for function parameters and return values
- **Error handling**: Use try/except blocks for error-prone operations

## Project Structure
- **uv-managed Python project** with virtual environment in `.venv/`
- Entry point: `main.py`
- Configuration: `pyproject.toml`
- Dependencies managed by uv with pytest and ruff installed

## Git Workflow
- **Commit frequently** - after each feature, phase, or significant change
- **Run linting before commits**: `uv run ruff check && uv run ruff format`
- **Descriptive commit messages** - explain what and why, not just what
- **Include opencode attribution** in commits when AI-assisted

## Project Overview
- **Snowflake Method writing assistant** using AI agents (DSPy + OpenAI)
- **Web interface** - React frontend + FastAPI backend
- **Structured AI output** using DSPy + Pydantic models for clean JSON generation
- **Multi-story management** with database storage
- **Advanced UX features**: Auto-generation, AI refinement system, rollback functionality, smart navigation
- **Implemented features**: Steps 1-6 generation, story CRUD, frontend UI, AI refinement, rollback system
- **Tech stack**: React 18 + TypeScript, FastAPI + SQLite, DSPy + OpenAI

## Development Commands
- **Start dev servers**: `./scripts/start-dev.sh` (API on :8000, Frontend on :5173)
- **Stop dev servers**: `./scripts/stop-dev.sh`
- **Check server status**: `./scripts/status-dev.sh`
- **Restart servers**: `./scripts/restart-dev.sh`

## Notes
- This is a uv-managed Python project (use `uv` commands, not pip)
- Virtual environment automatically managed by uv
- Testing and linting tools are configured and ready to use
- Requires `OPENAI_API_KEY` environment variable for AI features