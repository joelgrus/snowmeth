#!/usr/bin/env python
"""Script to run the Snowflake Method API server."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("snowmeth.api.app:app", host="0.0.0.0", port=8000, reload=True)
