#!/bin/bash

echo "🔍 Snowflake Method Environment Check"
echo "===================================="

# Track if any checks fail
FAILED=0

# Check Python 3.11+
echo -n "Python 3.11+: "
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo "✅ $PYTHON_VERSION"
    else
        echo "❌ $PYTHON_VERSION (need 3.11+)"
        FAILED=1
    fi
else
    echo "❌ Not found"
    FAILED=1
fi

# Check uv
echo -n "uv package manager: "
if command -v uv >/dev/null 2>&1; then
    UV_VERSION=$(uv --version | cut -d' ' -f2)
    echo "✅ $UV_VERSION"
else
    echo "❌ Not found (install with: pip install uv)"
    FAILED=1
fi

# Check Node.js 18+
echo -n "Node.js 18+: "
if command -v node >/dev/null 2>&1; then
    NODE_VERSION=$(node --version | sed 's/v//')
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        echo "✅ $NODE_VERSION"
    else
        echo "❌ $NODE_VERSION (need 18+)"
        FAILED=1
    fi
else
    echo "❌ Not found"
    FAILED=1
fi

# Check npm
echo -n "npm: "
if command -v npm >/dev/null 2>&1; then
    NPM_VERSION=$(npm --version)
    echo "✅ $NPM_VERSION"
else
    echo "❌ Not found"
    FAILED=1
fi

# Check OpenAI API key
echo -n "OPENAI_API_KEY: "
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ Set"
else
    echo "⚠️  Not set (AI features will not work)"
fi

# Check if project dependencies are installed
echo -n "Python dependencies: "
if [ -d ".venv" ] && uv run python -c "import fastapi" 2>/dev/null; then
    echo "✅ Installed"
else
    echo "❌ Not installed (run: make install)"
    FAILED=1
fi

echo -n "Frontend dependencies: "
if [ -d "frontend/node_modules" ]; then
    echo "✅ Installed"
else
    echo "❌ Not installed (run: make install)"
    FAILED=1
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "🎉 Environment check passed! Ready to run 'make dev'"
else
    echo "❌ Environment check failed. Please fix the issues above."
    echo ""
    echo "Quick setup:"
    echo "1. Install missing dependencies"
    echo "2. Set OPENAI_API_KEY environment variable"
    echo "3. Run: make setup"
fi

exit $FAILED