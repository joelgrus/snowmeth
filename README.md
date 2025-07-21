# Snowflake Method - Writing Assistant

An AI-powered web application that "guides" writers through [Randy Ingermanson's 10-step Snowflake Method](https://www.advancedfictionwriting.com/articles/snowflake-method/) for novel planning. (The AI does most of the work.)

Currently it doesn't do Step 10 ("write the novel"), I have to think about how to make that happen. Instead it lets you download Steps 1-9 as a PDF.

## Features

### Core Functionality
- **AI-Guided Story Development**: Step-by-step progression through the Snowflake Method
- **Smart Content Generation**: OpenAI-powered generation for each step using DSPy structured output
- **Multi-Story Management**: Create, manage, and organize multiple story projects
- **Rich Text Editing**: Specialized editors for different content types (characters, plot structure, synopses)

### Advanced UX Features
- **Seamless Workflow**: Auto-generation when advancing steps (no extra clicks)
- **Animated Feedback**: Pulsing robot animations and visual feedback during AI generation
- **Smart Navigation**: Previous/Next buttons for completed steps, single "Accept & Continue" for progression
- **AI-Assisted Refinement**: Inline refinement system with natural language instructions
- **Rollback System**: Reset to previous steps with automatic clearing of dependent future work
- **Progress Protection**: Intelligent warnings when actions will affect future content

### Technical Features
- **Dual Interface**: Web UI + CLI for different workflows
- **Real-time Updates**: Responsive interface with loading states and success feedback
- **Structured AI Output**: Clean JSON generation using DSPy + Pydantic models
- **Async Architecture**: FastAPI backend with async SQLite storage

## Quick Start

### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone <repository>
cd snowmeth

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Start with Docker
make docker-up
```

That's it! Visit http://localhost:5173 to access the web interface.

### Option 2: Local Development
```bash
# Clone the repository
git clone <repository>
cd snowmeth

# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Complete setup and start development
make setup && make dev
```

Visit http://localhost:5173 to access the web interface.

### Prerequisites

**For Docker (Option 1):**
- Docker and Docker Compose
- OpenAI API key

**For Local Development (Option 2):**
- Python 3.11+
- Node.js 18+ 
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- OpenAI API key

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

### CLI Usage
```bash
# Start a new story
uv run snowmeth create "My Story Idea"

# Continue working on a story
uv run snowmeth work

# Generate content for current step
uv run snowmeth generate

# Refine existing content
uv run snowmeth refine "make this more dramatic"
```

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

## Credits

- **Snowflake Method** created by [Randy Ingermanson](https://www.advancedfictionwriting.com/) - the original novel planning methodology this tool implements
- **AI Content Generation** powered by OpenAI and DSPy framework
- Built with modern web technologies and a focus on writer experience

## License

[Add your license here]