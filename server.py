"""
Reachy Mini MCP Server

A Model Context Protocol (MCP) server for controlling the Reachy Mini robot.
This server provides tools to control the robot's head, antennas, camera, and more.

The server communicates with the Reachy Mini daemon running on localhost:8000.

This version uses a repository-based approach for defining tools dynamically.
"""

import httpx
import json
import os
import math
import asyncio
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Reachy Mini Controller")

# Configuration
REACHY_BASE_URL = "http://localhost:8000"
TOOLS_REPOSITORY_PATH = Path(__file__).parent / "tools_repository"


# Helper functions
def create_head_pose(
    x: float = 0.0,
    y: float = 0.0, 
    z: float = 0.0,
    roll: float = 0.0,
    pitch: float = 0.0,
    yaw: float = 0.0,
    degrees: bool = False,
    mm: bool = False
) -> Dict[str, Any]:
    """
    Create a head pose configuration for Reachy Mini.
    
    Args:
        x, y, z: Position offsets (meters by default, mm if mm=True)
        roll, pitch, yaw: Rotation angles (radians by default, degrees if degrees=True)
        degrees: If True, angles are in degrees
        mm: If True, positions are in millimeters
    
    Returns:
        Dictionary with head pose configuration
    """
    if mm:
        x, y, z = x / 1000, y / 1000, z / 1000
    
    if degrees:
        roll = math.radians(roll)
        pitch = math.radians(pitch)
        yaw = math.radians(yaw)
    
    return {
        "x": x,
        "y": y,
        "z": z,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw
    }


async def make_request(
    method: str,
    endpoint: str,
    json_data: Optional[Dict] = None,
    params: Optional[Dict] = None
) -> Dict[str, Any]:
    """Make an HTTP request to the Reachy Mini daemon."""
    url = f"{REACHY_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            if method.upper() == "GET":
                response = await client.get(url, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, json=json_data)
            elif method.upper() == "PUT":
                response = await client.put(url, json=json_data)
            elif method.upper() == "DELETE":
                response = await client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {"status": "success"}
            
        except httpx.HTTPError as e:
            return {"error": str(e), "status": "failed"}


# Dynamic tool loading functions

def load_tool_index() -> Dict[str, Any]:
    """Load the tool index from tools_index.json."""
    index_path = TOOLS_REPOSITORY_PATH / "tools_index.json"
    if not index_path.exists():
        raise FileNotFoundError(f"Tool index not found at {index_path}")
    
    with open(index_path, 'r') as f:
        return json.load(f)


def load_tool_definition(definition_file: str) -> Dict[str, Any]:
    """Load a tool definition from a JSON file."""
    def_path = TOOLS_REPOSITORY_PATH / definition_file
    if not def_path.exists():
        raise FileNotFoundError(f"Tool definition not found at {def_path}")
    
    with open(def_path, 'r') as f:
        return json.load(f)


def load_script_module(script_file: str):
    """Dynamically load a Python script as a module."""
    script_path = TOOLS_REPOSITORY_PATH / "scripts" / script_file
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found at {script_path}")
    
    spec = importlib.util.spec_from_file_location("tool_script", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_tool_function(tool_def: Dict[str, Any]):
    """Create a tool function from a tool definition."""
    import inspect
    
    # Map JSON types to Python types
    type_mapping = {
        "string": str,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict
    }
    
    # Build parameter list for function signature
    params = []
    annotations = {}
    required_params = tool_def.get("parameters", {}).get("required", [])
    optional_params = tool_def.get("parameters", {}).get("optional", [])
    
    # Add required parameters
    for param in required_params:
        param_name = param["name"]
        param_type = type_mapping.get(param["type"], Any)
        params.append(inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=param_type
        ))
        annotations[param_name] = param_type
    
    # Add optional parameters with defaults
    for param in optional_params:
        param_name = param["name"]
        default_value = param.get("default", None)
        param_type = Optional[type_mapping.get(param["type"], Any)]
        params.append(inspect.Parameter(
            param_name,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=default_value,
            annotation=param_type
        ))
        annotations[param_name] = param_type
    
    execution = tool_def.get("execution", {})
    exec_type = execution.get("type")
    
    if exec_type == "script":
        # Load the script module
        script_file = execution.get("script_file")
        module = load_script_module(script_file)
        
        async def tool_func_impl(*args, **kwargs):
            # Call the execute function from the script
            return await module.execute(make_request, create_head_pose, kwargs)
        
        # Create a new function with the proper signature and annotations
        tool_func_impl.__signature__ = inspect.Signature(params)
        tool_func_impl.__annotations__ = annotations
        return tool_func_impl
    
    else:
        raise ValueError(f"Unknown execution type: {exec_type}. Only 'script' type is supported.")


def register_tools_from_repository():
    """Load and register all tools from the repository."""
    try:
        index = load_tool_index()
        
        for tool_entry in index.get("tools", []):
            # Skip disabled tools
            if not tool_entry.get("enabled", True):
                continue
            
            tool_name = tool_entry.get("name")
            definition_file = tool_entry.get("definition_file")
            
            try:
                # Load tool definition
                tool_def = load_tool_definition(definition_file)
                
                # Create the tool function
                tool_func = create_tool_function(tool_def)
                
                # Set the function name and docstring
                tool_func.__name__ = tool_name
                tool_func.__doc__ = tool_def.get("description", "")
                
                # Only register in the global registry for operate_robot tool
                # Individual tools are NOT registered as MCP tools - only operate_robot is exposed
                register_tool_to_registry(tool_name, tool_func)
                
                print(f"✓ Loaded tool to registry: {tool_name}")
                
            except Exception as e:
                import traceback
                print(f"✗ Failed to register tool {tool_name}: {e}")
                print(f"  Traceback: {traceback.format_exc()}")
        
        print(f"\n✓ Successfully loaded {len([t for t in index.get('tools', []) if t.get('enabled', True)])} tools to registry")
        print(f"✓ Tool registry contains {len(TOOL_REGISTRY)} tools available for operate_robot")
        
    except Exception as e:
        print(f"✗ Failed to load tools from repository: {e}")
        raise


# Resources

@mcp.resource("reachy://status")
async def get_status_resource() -> str:
    """Get robot status as a formatted resource."""
    state = await make_request("GET", "/api/state/full")
    return f"Reachy Mini Status:\n{json.dumps(state, indent=2)}"


@mcp.resource("reachy://capabilities")
async def get_capabilities_resource() -> str:
    """Get a description of robot capabilities."""
    return """
Reachy Mini Capabilities:

MOVEMENT:
- 3-DOF head movement (x, y, z position + roll, pitch, yaw orientation)
- 2 expressive antennas (independent control)

SENSORS:
- Camera for vision tasks
- Motor position feedback

EMOTIONS & GESTURES:
- Express emotions: happy, sad, curious, surprised, confused
- Perform gestures: greeting, yes, no, thinking, celebration
- Look in directions: up, down, left, right, forward

CONTROL:
- Power management (on/off)
- Emergency stop
- Real-time state monitoring
"""


# Prompts

@mcp.prompt()
def control_prompt() -> str:
    """Prompt for controlling Reachy Mini."""
    return """
You are controlling a Reachy Mini robot. The robot has:
- A movable head with 3D position and orientation control
- Two expressive antennas
- A camera for vision
- Various gestures and emotion expressions

AVAILABLE MCP TOOLS (5 total):

Status Tools (4):
1. get_robot_state() - Get full robot state
2. get_health_status() - Check robot health
3. get_power_state() - Check if robot is on/off
4. turn_on_robot() - Power on the robot

Control Tool (1):
5. operate_robot() - Execute robot commands based on body parts

The operate_robot() tool uses a simplified interface where you specify the bodyPart and its parameters:

Examples:
- Move head: operate_robot(commands=[{"bodyPart": "head", "z": 10, "duration": 2.0}])
- Express emotion: operate_robot(commands=[{"bodyPart": "emotion", "emotion": "happy"}])
- Perform gesture: operate_robot(commands=[{"bodyPart": "gesture", "gesture": "greeting"}])
- Control antennas: operate_robot(commands=[{"bodyPart": "antennas", "left": 30, "right": -30, "duration": 1.5}])
- Nod head: operate_robot(commands=[{"bodyPart": "nod", "angle": 15, "duration": 1.0}])
- Look around: operate_robot(commands=[{"bodyPart": "look", "direction": "left", "duration": 1.0}])

Command Sequences (execute multiple actions):
operate_robot(commands=[
    {"bodyPart": "gesture", "gesture": "greeting"},
    {"bodyPart": "nod", "angle": 15, "duration": 2.0},
    {"bodyPart": "antennas", "left": 30, "right": -30, "duration": 1.5}
])

Best Practices:
- Always check robot state first with get_robot_state()
- Ensure robot is powered on with turn_on_robot() before movement commands
- Use command sequences for complex choreographed movements

Available Body Parts:
- head: Move head (x, y, z, roll, pitch, yaw, duration)
- antennas: Move antennas (left, right, duration)
- emotion: Express emotion (emotion: happy/sad/curious/surprised/confused)
- gesture: Perform gesture (gesture: greeting/yes/no/thinking/celebration)
- nod: Nod head (angle, duration)
- shake: Shake head (angle, duration)
- tilt: Tilt head (direction, angle, duration)
- look: Look in direction (direction: up/down/left/right/forward, duration)
- power: Control power (state: on/off)
- reset_head: Reset head to neutral
- reset_antennas: Reset antennas to neutral
- state: Get robot state
- head_state: Get head state
- antennas_state: Get antenna state
- power_state: Get power state
- health: Get health status
- stop: Stop all movements
"""


@mcp.prompt()
def safety_prompt() -> str:
    """Safety guidelines for robot control."""
    return """
Reachy Mini Safety Guidelines:

1. Always check robot state before issuing movement commands using get_robot_state()
2. Use appropriate durations (typically 1-3 seconds) for smooth movements
3. Avoid extreme angles that might stress the motors
4. Use operate_robot(commands=[{"bodyPart": "stop"}]) in case of unexpected behavior
5. Turn off the robot with operate_robot(commands=[{"bodyPart": "power", "state": "off"}]) when done
6. Monitor health_status periodically during extended use with get_health_status()
7. When using command sequences, ensure movements have appropriate durations to complete before the next command

Head Position Limits:
- Position offsets: typically ±20mm on x/y/z
- Rotation angles: ±45 degrees for safe operation

Antenna Limits:
- Typical range: -45 to 45 degrees

Command Sequences:
- Commands in a sequence are executed sequentially
- Each command waits for the previous one to complete
- If a command fails, subsequent commands will still be attempted
- Check the results array to see which commands succeeded or failed

Available Body Parts for operate_robot:
- Movement: head, nod, shake, tilt, reset_head
- Antennas: antennas, reset_antennas, antennas_state
- Expressions: emotion, gesture, look
- Control: power, stop
- Status: state, head_state, health, power_state
"""


# Tool registry for dynamic tool execution
TOOL_REGISTRY = {}

def register_tool_to_registry(tool_name: str, tool_func):
    """Register a tool in the global registry for dynamic execution."""
    TOOL_REGISTRY[tool_name] = tool_func


def get_tool_registry() -> Dict[str, Any]:
    """Get the current tool registry. Ensures it's loaded."""
    if not TOOL_REGISTRY:
        # This shouldn't happen if initialize_server was called
        # but provides a safety net
        print("WARNING: Tool registry is empty. This should not happen in normal operation.")
    return TOOL_REGISTRY


# Meta-tool for operating the robot dynamically
# Note: This is registered manually in initialize_server() after all tools are loaded
async def operate_robot(
    commands: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Execute robot control commands based on body parts and parameters.
    
    Simplified interface that accepts a list of control commands, where each command
    specifies a bodyPart and its control parameters.
    
    Args:
        commands: List of command dictionaries. Each dict should contain:
                  - "bodyPart": The body part to control (head, antennas, emotion, gesture, etc.)
                  - Additional parameters specific to that body part
    
    Body Parts and Parameters:
        - head: x, y, z, roll, pitch, yaw, duration (move head)
        - antennas: left, right, duration (move antennas)
        - emotion: emotion (happy/sad/curious/surprised/confused)
        - gesture: gesture (greeting/yes/no/thinking/celebration)
        - nod: angle, duration (nod head)
        - shake: angle, duration (shake head)
        - tilt: direction, angle, duration (tilt head)
        - look: direction (up/down/left/right/forward), duration
        - power: state (on/off)
    
    Returns:
        Dictionary with results from all commands
        
    Examples:
        # Move head and antennas
        operate_robot(commands=[
            {"bodyPart": "head", "z": 10, "duration": 2.0},
            {"bodyPart": "antennas", "left": 30, "right": -30, "duration": 1.5}
        ])
        
        # Express emotion and gesture
        operate_robot(commands=[
            {"bodyPart": "emotion", "emotion": "happy"},
            {"bodyPart": "gesture", "gesture": "greeting"}
        ])
        
        # Nod and look
        operate_robot(commands=[
            {"bodyPart": "nod", "angle": 15, "duration": 1.0},
            {"bodyPart": "look", "direction": "left", "duration": 1.0}
        ])
    """
    # Get the current tool registry
    registry = get_tool_registry()
    
    # Mapping from bodyPart to tool names
    BODY_PART_TO_TOOL = {
        "head": "move_head",
        "antennas": "move_antennas",
        "emotion": "express_emotion",
        "gesture": "perform_gesture",
        "nod": "nod_head",
        "shake": "shake_head",
        "tilt": "tilt_head",
        "look": "look_at_direction",
        "power": None,  # Special handling
        "reset_head": "reset_head",
        "reset_antennas": "reset_antennas",
        "state": "get_robot_state",
        "head_state": "get_head_state",
        "antennas_state": "get_antennas_state",
        "power_state": "get_power_state",
        "health": "get_health_status",
        "stop": "stop_all_movements"
    }
    
    if not isinstance(commands, list):
        return {
            "error": "commands parameter must be a list of command dictionaries",
            "status": "failed"
        }
    
    results = []
    failed_count = 0
    
    for idx, command in enumerate(commands):
        if not isinstance(command, dict):
            results.append({
                "command_index": idx,
                "error": "Each command must be a dictionary",
                "status": "failed"
            })
            failed_count += 1
            continue
        
        body_part = command.get("bodyPart")
        
        if not body_part:
            results.append({
                "command_index": idx,
                "error": "Missing 'bodyPart' in command",
                "available_body_parts": list(BODY_PART_TO_TOOL.keys()),
                "status": "failed"
            })
            failed_count += 1
            continue
        
        # Map bodyPart to tool name
        tool_name = BODY_PART_TO_TOOL.get(body_part)
        
        # Special handling for power
        if body_part == "power":
            state = command.get("state", "").lower()
            if state == "on":
                tool_name = "turn_on_robot"
            elif state == "off":
                tool_name = "turn_off_robot"
            else:
                results.append({
                    "command_index": idx,
                    "bodyPart": body_part,
                    "error": "Power state must be 'on' or 'off'",
                    "status": "failed"
                })
                failed_count += 1
                continue
        
        if not tool_name:
            results.append({
                "command_index": idx,
                "bodyPart": body_part,
                "error": f"Unknown bodyPart '{body_part}'",
                "available_body_parts": list(BODY_PART_TO_TOOL.keys()),
                "status": "failed"
            })
            failed_count += 1
            continue
        
        # Check if tool exists in registry
        if tool_name not in registry:
            results.append({
                "command_index": idx,
                "bodyPart": body_part,
                "tool_name": tool_name,
                "error": f"Tool '{tool_name}' not found in registry",
                "status": "failed"
            })
            failed_count += 1
            continue
        
        # Extract parameters (everything except bodyPart)
        parameters = {k: v for k, v in command.items() if k != "bodyPart"}
        
        # Execute the command
        try:
            tool_func = registry[tool_name]
            result = await tool_func(**parameters)
            results.append({
                "command_index": idx,
                "bodyPart": body_part,
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "command_index": idx,
                "bodyPart": body_part,
                "tool": tool_name,
                "parameters": parameters,
                "error": str(e),
                "status": "failed"
            })
            failed_count += 1
    
    return {
        "total_commands": len(commands),
        "successful": len(commands) - failed_count,
        "failed": failed_count,
        "results": results,
        "status": "success" if failed_count == 0 else "partial" if failed_count < len(commands) else "failed"
    }


# Initialize and run

def initialize_server():
    """Initialize the server by loading all tools from the repository."""
    print("=" * 60)
    print("Reachy Mini MCP Server - Minimal Tool Set (5 Tools)")
    print("=" * 60)
    print(f"Tools repository path: {TOOLS_REPOSITORY_PATH}")
    print(f"Reachy daemon URL: {REACHY_BASE_URL}")
    print("-" * 60)
    
    # Register all tools from repository into the internal registry
    # These are used by operate_robot but not exposed as individual MCP tools
    register_tools_from_repository()
    
    # Register ONLY 5 essential MCP tools:
    # 1. operate_robot - meta-tool for executing any command or command sequence
    mcp.tool()(operate_robot)
    print("✓ Registered MCP tool: operate_robot (meta-tool for all robot operations)")
    
    # 2-5. Status check tools exposed directly for convenience
    # These are the same functions from the registry but exposed as MCP tools
    registry = get_tool_registry()
    
    essential_status_tools = [
        "get_robot_state",
        "get_health_status", 
        "get_power_state",
        "turn_on_robot"
    ]
    
    for tool_name in essential_status_tools:
        if tool_name in registry:
            tool_func = registry[tool_name]
            mcp.tool()(tool_func)
            print(f"✓ Registered MCP tool: {tool_name}")
        else:
            print(f"✗ Warning: {tool_name} not found in registry")
    
    print("-" * 60)
    print(f"✓ Total MCP tools exposed: 5")
    print(f"✓ Tool registry contains {len(registry)} tools available for operate_robot")
    print("=" * 60)
    print("Server initialized and ready!")
    print("=" * 60)


if __name__ == "__main__":
    # Initialize the server and load all tools BEFORE FastMCP starts
    initialize_server()
    
    # Run the MCP server
    mcp.run()
else:
    # If imported as a module, initialize immediately
    initialize_server()
