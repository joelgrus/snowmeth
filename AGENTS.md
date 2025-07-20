# Agent Guidelines for snowmeth2

## Build/Test Commands
- **Run main script**: `uv run python main.py`
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

## Notes
- This is a uv-managed Python project (use `uv` commands, not pip)
- Virtual environment automatically managed by uv
- No existing Cursor/Copilot rules found
- Testing and linting tools are now configured and ready to use