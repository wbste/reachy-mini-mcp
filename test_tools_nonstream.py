#!/usr/bin/env python3
import asyncio
import httpx
import json

async def test():
    url = "http://localhost:8100/v1/chat/completions"
    
    # Test with tools
    tools = [{
        "type": "function",
        "function": {
            "name": "nod_head",
            "description": "Make the robot nod",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    }]
    
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": "Make the robot nod"}],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 100
    }
    
    print("Testing non-streaming with tools...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            print(json.dumps(result, indent=2))
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
