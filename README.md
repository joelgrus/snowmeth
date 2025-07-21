# Snowflake Method - Writing Assistant

An AI-powered web application that guides writers through [Randy Ingermanson's 10-step Snowflake Method](https://www.advancedfictionwriting.com/articles/snowflake-method/) for novel planning.

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

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Installation
```bash
# Clone and setup
git clone <repository>
cd snowmeth2

# Backend setup
uv sync
export OPENAI_API_KEY="your-key-here"

# Frontend setup
cd frontend && npm install

# Start development servers
./scripts/start-dev.sh
```

Visit http://localhost:5173 to access the web interface.

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