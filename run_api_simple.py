#!/usr/bin/env python
"""Simple script to run the API for testing."""

import uvicorn
from snowmeth.api.app_simple import app

if __name__ == "__main__":
    uvicorn.run("snowmeth.api.app_simple:app", host="0.0.0.0", port=8001, reload=True)