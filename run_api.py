#!/usr/bin/env python
"""Run the Snowflake Method API server."""

import uvicorn
from snowmeth.api.app import app

if __name__ == "__main__":
    print("Starting Snowflake Method API server...")
    print("Documentation will be available at: http://localhost:8000/docs")
    uvicorn.run(
        "snowmeth.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload for development
    )