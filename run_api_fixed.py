#!/usr/bin/env python
"""Script to run the fixed API for testing."""

import uvicorn
from snowmeth.api.app import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)