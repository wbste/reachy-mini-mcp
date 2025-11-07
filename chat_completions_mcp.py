#!/usr/bin/env python3
"""
Chat Completions with MCP Tool Integration (Non-Streaming)

This script demonstrates how to:
1. Initialize an MCP client and load tools from mcp.json
2. Make chat completion requests to http://localhost:8100/v1/chat/completions
3. Handle tool calls from the model
4. Execute tools via MCP server
5. Continue the conversation with tool results

Usage:
    python chat_completions_mcp.py
"""

import asyncio
import httpx
import json
from pathlib import Path
from typing import List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Configuration
CHAT_COMPLETIONS_URL = "http://localhost:8100/v1/chat/completions"
MODEL_NAME = "openai/gpt-oss-20b"  # Adjust based on your vLLM setup


class MCPChatClient:
    """Client for chat completions with MCP tool integration."""
    
    def __init__(self):
        self.mcp_session = None
        self.read_stream = None
        self.write_stream = None
        self.client_context = None
        self.stdio_context = None
        self.mcp_tools = []
        self.messages = []
        
    async def initialize_mcp(self):
        """Initialize MCP client and load tools from mcp.json."""
        print("=" * 70)
        print("Initializing MCP Client")
        print("=" * 70)
        
        # Load mcp.json configuration
        mcp_config_path = Path(__file__).parent / "mcp.json"
        with open(mcp_config_path, 'r') as f:
            mcp_config = json.load(f)
        
        server_config = mcp_config["mcpServers"]["reachy-mini"]
        
        print(f"\n📋 Server configuration:")
        print(f"   Command: {server_config['command']}")
        print(f"   Args: {server_config['args']}")
        
        # Initialize MCP client
        print("\n🚀 Starting MCP server...")
        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config["args"],
            env=server_config.get("env", {})
        )
        
        # Store contexts for later cleanup
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
        
        self.client_context = ClientSession(self.read_stream, self.write_stream)
        self.mcp_session = await self.client_context.__aenter__()
        
        # Initialize the session
        await self.mcp_session.initialize()
        print("   ✓ MCP session initialized")
        
        # List available tools
        print("\n🔧 Loading available tools...")
        tools_result = await self.mcp_session.list_tools()
        
        print(f"\n   Found {len(tools_result.tools)} tool(s):")
        for tool in tools_result.tools:
            print(f"   - {tool.name}")
            print(f"     {tool.description[:80]}...")
            
            # Convert MCP tool to OpenAI tool format
            openai_tool = self._convert_mcp_tool_to_openai(tool)
            self.mcp_tools.append({
                "mcp_tool": tool,
                "openai_tool": openai_tool
            })
        
        print("\n" + "=" * 70)
        print(f"✓ MCP Client ready with {len(self.mcp_tools)} tools")
        print("=" * 70 + "\n")
        
    def _convert_mcp_tool_to_openai(self, mcp_tool) -> Dict[str, Any]:
        """Convert MCP tool definition to OpenAI tool format."""
        return {
            "type": "function",
            "function": {
                "name": mcp_tool.name,
                "description": mcp_tool.description,
                "parameters": mcp_tool.inputSchema if mcp_tool.inputSchema else {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            }
        }
    
    async def execute_tool_via_mcp(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool via MCP server."""
        print(f"\n🔧 Executing tool: {tool_name}")
        print(f"   Arguments: {json.dumps(arguments, indent=2)}")
        
        try:
            result = await self.mcp_session.call_tool(tool_name, arguments)
            print(f"   ✓ Tool executed successfully")
            return result
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            print(f"   ✗ {error_msg}")
            return {"error": error_msg}
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] = None,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Make a chat completion request (non-streaming)."""
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        print("\n📤 Sending chat completion request...")
        print(f"   Messages: {len(messages)}")
        if tools:
            print(f"   Tools: {len(tools)}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(CHAT_COMPLETIONS_URL, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Print response with buffer simulation
                self._print_response_with_buffer(result)
                
                return result
            except Exception as e:
                print(f"   ✗ Error: {e}")
                raise
    
    def _print_response_with_buffer(self, response: Dict[str, Any]):
        """Print response simulating token-by-token arrival with buffer."""
        print("\n" + "=" * 70)
        print("📥 Response from model:")
        print("=" * 70)
        
        if "choices" in response and len(response["choices"]) > 0:
            choice = response["choices"][0]
            message = choice.get("message", {})
            
            # Print content if available
            content = message.get("content")
            if content:
                print("\n💬 Content:")
                # Simulate token arrival by printing character by character
                import sys
                import time
                for char in content:
                    sys.stdout.write(char)
                    sys.stdout.flush()
                    time.sleep(0.01)  # Small delay to simulate streaming
                print("\n")
            
            # Print tool calls if available
            tool_calls = message.get("tool_calls")
            if tool_calls:
                print("🔧 Tool Calls:")
                for i, tool_call in enumerate(tool_calls):
                    print(f"\n   [{i+1}] {tool_call.get('function', {}).get('name')}")
                    args = tool_call.get('function', {}).get('arguments')
                    if args:
                        # Parse if string
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except:
                                pass
                        print(f"       Arguments: {json.dumps(args, indent=8)}")
            
            # Print finish reason
            finish_reason = choice.get("finish_reason")
            if finish_reason:
                print(f"\n✓ Finish reason: {finish_reason}")
        
        # Print usage stats
        if "usage" in response:
            usage = response["usage"]
            print(f"\n📊 Usage:")
            print(f"   Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"   Completion tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        print("=" * 70 + "\n")
    
    async def run_conversation(self, user_message: str):
        """Run a conversation with tool support."""
        print("\n" + "=" * 70)
        print("Starting Conversation")
        print("=" * 70)
        
        # Initialize conversation with user message
        self.messages = [
            {"role": "user", "content": user_message}
        ]
        
        print(f"\n👤 User: {user_message}\n")
        
        # Get OpenAI-formatted tools
        openai_tools = [tool_dict["openai_tool"] for tool_dict in self.mcp_tools]
        
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n{'='*70}")
            print(f"Iteration {iteration}")
            print(f"{'='*70}")
            
            # Make chat completion request
            response = await self.chat_completion(
                messages=self.messages,
                tools=openai_tools
            )
            
            # Get the assistant's message
            choice = response["choices"][0]
            assistant_message = choice["message"]
            finish_reason = choice["finish_reason"]
            
            # Add assistant message to conversation
            self.messages.append(assistant_message)
            
            # Check if we're done
            if finish_reason == "stop":
                print("\n✓ Conversation completed!")
                break
            
            # Check if response was truncated
            if finish_reason == "length":
                print("\n⚠️  Response was truncated due to max_tokens limit")
                print("✓ Conversation completed (truncated)")
                break
            
            # Handle tool calls
            if finish_reason == "tool_calls" and "tool_calls" in assistant_message:
                tool_calls = assistant_message["tool_calls"]
                
                print(f"\n🔧 Processing {len(tool_calls)} tool call(s)...")
                
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_call_id = tool_call.get("id")
                    function = tool_call.get("function", {})
                    tool_name = function.get("name")
                    arguments_str = function.get("arguments", "{}")
                    
                    # Parse arguments
                    try:
                        arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # Execute tool via MCP
                    tool_result = await self.execute_tool_via_mcp(tool_name, arguments)
                    
                    # Format tool result
                    tool_result_content = json.dumps(tool_result.model_dump() if hasattr(tool_result, 'model_dump') else tool_result)
                    
                    # Add tool result to conversation
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "name": tool_name,
                        "content": tool_result_content
                    })
                    
                    print(f"   ✓ Added tool result to conversation")
                
                # Continue conversation with tool results
                continue
            
            # If we get here with a different finish reason, something unexpected happened
            print(f"\n⚠️  Unexpected finish reason: {finish_reason}")
            break
        
        if iteration >= max_iterations:
            print(f"\n⚠️  Reached maximum iterations ({max_iterations})")
        
        print("\n" + "=" * 70)
        print("Conversation Summary")
        print("=" * 70)
        print(f"Total messages: {len(self.messages)}")
        print(f"Iterations: {iteration}")
        print("=" * 70 + "\n")
    
    async def cleanup(self):
        """Cleanup MCP session."""
        print("\n🧹 Cleaning up...")
        if self.client_context:
            await self.client_context.__aexit__(None, None, None)
        if self.stdio_context:
            await self.stdio_context.__aexit__(None, None, None)
        print("   ✓ Cleanup complete")


async def main():
    """Main function."""
    print("\n" + "=" * 70)
    print("Chat Completions with MCP Tool Integration")
    print("=" * 70)
    print("\nThis script will:")
    print("1. Initialize MCP client from mcp.json")
    print("2. Load available tools")
    print("3. Send chat completion request with tools")
    print("4. Execute tools via MCP when model requests them")
    print("5. Continue conversation until completion")
    print("\nMake sure:")
    print("  - Reachy Mini daemon is running (reachy-mini-daemon)")
    print("  - vLLM server is running on http://localhost:8100")
    print("=" * 70 + "\n")
    
    client = MCPChatClient()
    
    try:
        # Initialize MCP
        await client.initialize_mcp()
        
        # Example conversations - uncomment one to test
        
        # Simple greeting
        # await client.run_conversation("Hello! Can you make the robot wave?")
        
        # Get robot state
        # await client.run_conversation("What is the current state of the robot?")
        
        # Complex interaction
        await client.run_conversation(
            "Please do the following: First, turn on the robot. "
            "Then make it perform a greeting gesture. "
            "After that, make it nod its head. "
            "Finally, tell me the robot's current state."
        )
        
        # Express emotion
        # await client.run_conversation("Make the robot express happiness")
        
        # Multiple operations
        # await client.run_conversation(
        #     "Make the robot look left, then right, then return to center. "
        #     "After that, make it nod to confirm."
        # )
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.cleanup()
    
    print("\n✅ Done!\n")


if __name__ == "__main__":
    asyncio.run(main())
