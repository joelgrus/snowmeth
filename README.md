# Snowflake Method - Writing Assistant

An AI-powered web application that guides writers through all 10 steps of [Randy Ingermanson's Snowflake Method](https://www.advancedfictionwriting.com/articles/snowflake-method/) for novel planning and writing. (The AI does most of the work.)

**Complete Implementation**: All 10 steps are now supported, including Step 10 which generates your novel chapter-by-chapter with style consistency and refinement capabilities.

## Features

### Core Functionality
- **Complete 10-Step Implementation**: Full Snowflake Method from initial concept to finished novel
- **AI-Guided Story Development**: Step-by-step progression through the Snowflake Method
- **Chapter-by-Chapter Novel Generation**: Step 10 generates full novel chapters with style consistency
- **Smart Content Generation**: OpenAI-powered generation for each step using DSPy structured output
- **Multi-Story Management**: Create, manage, and organize multiple story projects
- **Rich Text Editing**: Specialized editors for different content types (characters, plot structure, synopses)

### Advanced UX Features
- **Seamless Workflow**: Auto-generation when advancing steps (no extra clicks)
- **Animated Feedback**: Pulsing robot animations and visual feedback during AI generation
- **Smart Navigation**: Previous/Next buttons for completed steps, single "Accept & Continue" for progression
- **AI-Assisted Refinement**: Inline refinement system with natural language instructions for both planning content and novel chapters
- **Sequential Chapter Generation**: Enforced chapter order with automatic invalidation of dependent chapters
- **Writing Style Consistency**: AI matches writing style across chapters for coherent narrative voice
- **Chapter Management**: Progress tracking, word counts, and selective chapter refinement
- **Rollback System**: Reset to previous steps with automatic clearing of dependent future work
- **Progress Protection**: Intelligent warnings when actions will affect future content

### Technical Features
- **Web Interface**: Modern React frontend with TypeScript
- **Real-time Updates**: Responsive interface with loading states and success feedback
- **Structured AI Output**: Clean JSON generation using DSPy + Pydantic models
- **Async Architecture**: FastAPI backend with async SQLite storage

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone https://github.com/joelgrus/snowmeth.git
cd snowmeth

# Set your API keys (required)
export OPENAI_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"  # Optional, for alternative models

# Start with Docker
make docker-up
```

That's it! Visit http://localhost:5173 to access the web interface.

### Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/joelgrus/snowmeth.git
cd snowmeth

# Set your API keys (required)
export OPENAI_API_KEY="your-key-here"
export OPENROUTER_API_KEY="your-key-here"  # Optional, for alternative models

# Complete setup and start development
make setup && make dev
```

Visit http://localhost:5173 to access the web interface.

### Prerequisites

**For Docker (Option 1):**
- Docker and Docker Compose
- OpenAI API key (or OpenRouter API key for alternative models)

**For Local Development (Option 2):**
- Python 3.11+
- Node.js 18+ 
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- OpenAI API key (or OpenRouter API key for alternative models)

### Docker Commands
```bash
make docker-build  # Build Docker images
make docker-up     # Start containers
make docker-down   # Stop containers
make docker-logs   # View logs
make docker-shell  # Open shell in API container
make docker-test   # Run tests in Docker
make docker-clean  # Remove images and volumes
```

### Development Commands
Run `make help` to see all available commands, or use these common ones:

```bash
make setup    # Complete project setup
make dev      # Start development servers  
make test     # Run tests
make lint     # Check code quality
make clean    # Clean build artifacts
```

### Manual Installation (if you prefer)
```bash
# Backend setup
uv sync
export OPENAI_API_KEY="your-key-here"

# Frontend setup  
cd frontend && npm install

# Start development servers
./scripts/start-dev.sh
```

## Model Configuration

The application uses OpenAI's `gpt-4o-mini` model by default, but you can customize this behavior:

### Using .env File (Recommended)
Create a `.env` file in the project root to override the default model:

```bash
# Use OpenRouter with Gemini
SNOWMETH_DEFAULT_MODEL=openrouter/google/gemini-2.5-flash-lite-preview-06-17
OPENROUTER_API_KEY=your-openrouter-key

# Or use a different OpenAI model
SNOWMETH_DEFAULT_MODEL=openai/gpt-4o
OPENAI_API_KEY=your-openai-key
```

### Environment Variable Override
You can also set the model via environment variable:

```bash
export SNOWMETH_DEFAULT_MODEL="openrouter/google/gemini-2.5-flash-lite-preview-06-17"
```

### Supported Models
The application automatically configures appropriate token limits for:
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, etc.
- **OpenRouter**: Any model available through OpenRouter (Anthropic, Google, etc.)
- **Anthropic**: `claude-3.5-sonnet`, `claude-3-opus` (via OpenRouter or direct API)
- **Google**: `gemini-2.5-pro`, `gemini-2.5-flash-lite` (via OpenRouter)

> **Note**: Some models may require specific API keys. For OpenRouter models, you'll need an OpenRouter API key instead of (or in addition to) an OpenAI key.

## The Snowflake Method Steps

The [Snowflake Method](https://www.advancedfictionwriting.com/articles/snowflake-method/) is a proven approach to novel planning created by Randy Ingermanson:

1. **Story Idea** - One-sentence story summary
2. **Paragraph Summary** - Expand to full paragraph
3. **Character List** - Main characters and roles
4. **Plot Structure** - Story structure and major plot points
5. **Character Synopses** - One-page description per main character
6. **Detailed Synopsis** - Four-page story synopsis
7. **Character Charts** - Detailed character development
8. **Scene Table** - Scene-by-scene breakdown
9. **Character Arcs** - Individual character storylines
10. **First Draft** - Ready to write!

> Learn more about the method and Randy's work at [AdvancedFictionWriting.com](https://www.advancedfictionwriting.com/)

## Architecture

### Backend (`snowmeth/`)
- **FastAPI** - Async web framework
- **SQLAlchemy + SQLite** - Async database with JSON support
- **DSPy + OpenAI** - Structured AI content generation
- **Click** - CLI interface

### Frontend (`frontend/`)
- **React 18** - Modern component architecture
- **TypeScript** - Type-safe development
- **Vite** - Fast development and building
- **CSS Modules** - Component-scoped styling

### Development Workflow
```bash
# Start both servers
./scripts/start-dev.sh

# Check status
./scripts/status-dev.sh

# Stop servers
./scripts/stop-dev.sh

# Run tests
uv run pytest

# Lint and format
uv run ruff check && uv run ruff format
```

## Contributing

See `TODO.md` for current development priorities and `CLAUDE.md` for development guidelines.

## Built By

**Joel Grus** - AI Engineer & Author
- 🐦 Twitter: [@joelgrus](https://twitter.com/joelgrus)
- 💼 LinkedIn: [/in/joelgrus](https://linkedin.com/in/joelgrus)
- 💻 GitHub: [joelgrus/snowmeth](https://github.com/joelgrus/snowmeth)

## Credits

- **Snowflake Method** created by [Randy Ingermanson](https://www.advancedfictionwriting.com/) - the original novel planning methodology this tool implements
- **AI Content Generation** powered by OpenAI and DSPy framework
- Built with modern web technologies and a focus on writer experience

## License

[Add your license here]