# Snowflake Method Project TODO

## ✅ Completed Tasks

### Frontend & Architecture
- [x] Plan front-end UX design and architecture
- [x] Create detailed frontend technical specifications  
- [x] Choose frontend framework and set up project structure
- [x] Implement core frontend components and routing
- [x] Build step-specific editors
- [x] Implement Step 3: Character List Editor
- [x] Implement Steps 4-6: Rich Text Editors
- [x] Add step navigation functionality
- [x] Extract reusable components
- [x] Create reusable hooks
- [x] Add CSS modules for styling
- [x] Create constants and types
- [x] Complete migration to refactored codebase
- [x] Clean up debugging code and do code review

### Backend & API
- [x] Fix API design with specific generation endpoints
- [x] Implement Accept/Regenerate functionality
- [x] Add generation endpoints for Steps 2-6
- [x] Add new story creation functionality
- [x] Add delete story functionality
- [x] Fix JSON generation using DSPy structured output
- [x] Clean up overly prescriptive AI prompts
- [x] Clean up unused files and debug code

### UX Improvements & Advanced Features
- [x] Auto-generation on step advancement (no separate Generate button click)
- [x] Animated loading indicators (pulsing robot + thought bubble)
- [x] Rollback functionality to previous steps with future work clearing
- [x] AI-assisted refinement system for all generated content steps
- [x] Inline refinement UI with input field and smooth animations
- [x] Warning system when refining earlier steps that clears later steps
- [x] Automatic clearing of later steps when refining earlier steps
- [x] Improved step navigation UX (Previous/Next buttons, single Accept & Continue)
- [x] Clear button labeling (Reset to this step vs navigation)

## 🚧 Pending Tasks

### High Priority
- [ ] Fill in stubbed workflow methods

### Medium Priority  
- [ ] Implement Step 7: Character Charts Editor
- [ ] Implement Step 8: Scene Table Editor
- [ ] Implement real-time task management
- [ ] Add API authentication (simple API key)

### Low Priority
- [ ] Create API documentation and tests
- [ ] (Maybe/Later) Implement LLM-based impact detection for refinements

## 📝 Task Details

### Step 7: Character Charts Editor
- Create detailed character development charts
- Integrate with existing character data from Steps 3 & 5
- Implement specialized UI for character chart editing

### Step 8: Scene Table Editor  
- Create spreadsheet-like interface for scene management
- Scene breakdown and organization tools
- Scene details and pacing management


### Authentication
- Simple API key-based authentication
- Secure endpoint access
- User session management

### Documentation & Testing
- API documentation with OpenAPI/Swagger
- Unit tests for core functionality
- Integration tests for API endpoints
- User documentation and guides

## 🏗️ Architecture Notes

**Current Stack:**
- Backend: FastAPI with async SQLAlchemy + SQLite
- Frontend: React 18 + TypeScript + Vite + Tailwind CSS v3
- AI: DSPy + OpenAI with Pydantic structured output
- Storage: Async SQLite with proper JSON handling

**Key Components:**
- Single consolidated API (`snowmeth/api/app.py`)
- Clean React components with CSS modules
- Structured AI output using Pydantic models
- Development scripts for easy server management