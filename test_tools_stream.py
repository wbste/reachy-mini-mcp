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
        "max_tokens": 100,
        "stream": True
    }
    
    print("Testing STREAMING with tools...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream('POST', url, json=payload) as response:
                response.raise_for_status()
                print(f"Status: {response.status_code}\n")
                
                count = 0
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    if line == "data: [DONE]":
                        print("\n[DONE]")
                        break
                    
                    if line.startswith("data: "):
                        count += 1
                        data = line[6:]
                        obj = json.loads(data)
                        print(f"Chunk {count}:")
                        print(json.dumps(obj, indent=2))
                        print()
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
