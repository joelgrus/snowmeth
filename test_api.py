#!/usr/bin/env python
"""Simple test script for the API."""

import asyncio
import httpx
import json
import time

API_BASE = "http://localhost:8000"


async def test_api():
    """Test basic API functionality."""
    async with httpx.AsyncClient() as client:
        print("Testing Snowflake Method API...")
        
        # Test 1: List stories
        print("\n1. Listing stories...")
        response = await client.get(f"{API_BASE}/api/stories")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {data['total']} stories")
        
        # Test 2: Create a story
        print("\n2. Creating a new story...")
        response = await client.post(
            f"{API_BASE}/api/stories",
            json={
                "slug": "api-test-story",
                "story_idea": "A developer tests their new API and discovers it has gained sentience"
            }
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            task_data = response.json()
            task_id = task_data["task_id"]
            print(f"Task ID: {task_id}")
            
            # Wait for task completion
            print("Waiting for story creation...")
            for i in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)
                task_response = await client.get(f"{API_BASE}/api/tasks/{task_id}")
                if task_response.status_code == 200:
                    task_status = task_response.json()
                    print(f"Status: {task_status['status']} ({task_status.get('progress', 0)*100:.0f}%)")
                    if task_status['status'] == 'completed':
                        print(f"Story created: {task_status['result']['story_id']}")
                        story_id = task_status['result']['story_id']
                        break
                    elif task_status['status'] == 'failed':
                        print(f"Task failed: {task_status.get('error')}")
                        return
        
        # Test 3: Get story details
        if 'story_id' in locals():
            print(f"\n3. Getting story details for {story_id}...")
            response = await client.get(f"{API_BASE}/api/stories/{story_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                story = response.json()
                print(f"Story: {story['slug']}")
                print(f"Idea: {story['story_idea']}")
                print(f"Current step: {story['current_step']}")
                print(f"Step 1 content: {story['steps'].get('1', 'N/A')}")


if __name__ == "__main__":
    print("Make sure the API is running with: uv run python run_api.py")
    print("Press Ctrl+C to cancel\n")
    asyncio.run(test_api())