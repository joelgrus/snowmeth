# Testing Plan for snowmeth

## Current Status: Basic Tests ✅

We now have a basic test suite with **10 passing tests**:

- `tests/test_agents.py` - 4 tests for utility functions
- `tests/test_cli.py` - 3 tests for basic CLI functionality  
- `tests/test_project.py` - 3 tests for Story class functionality

## Test Coverage Summary

### ✅ Currently Tested
- Utility functions (JSON markdown cleaning)
- Basic CLI commands (help, status, list)
- Story class (creation, content access, step validation)

### ❌ Not Yet Tested (High Priority)
- **API endpoints** (all FastAPI routes)
- **Workflow logic** (step progression, content generation)
- **Agent functionality** (DSPy integrations, AI calls)
- **Database operations** (SQLite storage, async operations)
- **Error handling** (exception scenarios)
- **Integration tests** (full workflows)

## Recommended Test Structure

```
tests/
├── unit/
│   ├── test_agents.py        ✅ Basic utilities done
│   ├── test_workflow.py      ❌ Business logic
│   ├── test_storage.py       ❌ Database operations  
│   ├── test_cli.py          ✅ Basic CLI done
│   └── test_config.py        ❌ Configuration
├── integration/
│   ├── test_api.py           ❌ FastAPI endpoints
│   ├── test_workflows.py     ❌ End-to-end flows
│   └── test_database.py      ❌ DB integration
└── fixtures/
    ├── sample_stories.json    ❌ Test data
    └── mock_responses.json    ❌ AI mocks
```

## Next Testing Priorities

### Phase 1 - Core Functionality
1. **API Testing** - Test all FastAPI endpoints
2. **Workflow Testing** - Test step progression logic
3. **Database Testing** - Test SQLite operations

### Phase 2 - Integration  
1. **Mock AI calls** - Test without hitting external APIs
2. **End-to-end flows** - Full story creation to completion
3. **Error scenarios** - Network failures, invalid data

### Phase 3 - Advanced
1. **Performance tests** - Large story handling
2. **Concurrency tests** - Multiple users
3. **Security tests** - Input validation

## Testing Tools & Setup

- **Framework**: pytest (already configured)
- **Async testing**: pytest-asyncio (for API tests)
- **Mocking**: pytest-mock (for AI calls)
- **Coverage**: pytest-cov (track coverage)
- **Fixtures**: Use for consistent test data

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=snowmeth

# Run specific test file
uv run pytest tests/test_agents.py -v

# Run and show warnings
uv run pytest -W default
```

## Warnings to Address

Current warnings about Pydantic v1 validators should be upgraded to v2:
- Replace `@validator` with `@field_validator`
- Update validation syntax in `agents.py`

## Test Data Needs

- Sample story data at different steps
- Mock AI responses for testing
- Invalid input scenarios
- Edge cases (empty content, malformed JSON)

## Estimated Testing Effort

- **Basic Coverage**: 1-2 days (API + Workflow tests)
- **Full Coverage**: 1 week (including integration tests)
- **Production Ready**: 2 weeks (including performance, security)

The foundation is now in place - we have a working test suite that validates our recent cleanup work!