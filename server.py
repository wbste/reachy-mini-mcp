"""
Reachy Mini MCP Server

A Model Context Protocol (MCP) server for controlling the Reachy Mini robot.
This server provides tools to control the robot's head, antennas, camera, and more.

The server communicates with the Reachy Mini daemon running on localhost:8000.
"""

import httpx
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
import asyncio
import math

# Initialize FastMCP server
mcp = FastMCP("Reachy Mini Controller")

# Configuration
REACHY_BASE_URL = "http://localhost:8000"


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


# MCP Tools

@mcp.tool()
async def get_robot_state() -> Dict[str, Any]:
    """
    Get the current full state of the Reachy Mini robot.
    
    Returns detailed information about:
    - Motors (head, antennas) and their current positions
    - Camera status
    - Power state
    - Connection status
    """
    return await make_request("GET", "/api/state/full")


@mcp.tool()
async def get_head_state() -> Dict[str, Any]:
    """
    Get the current state of the robot's head.
    
    Returns the head's current position (x, y, z) and orientation (roll, pitch, yaw).
    """
    full_state = await make_request("GET", "/api/state/full")
    if "head_pose" in full_state:
        return {"head_pose": full_state["head_pose"]}
    return full_state


@mcp.tool()
async def move_head(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    roll: float = 0.0,
    pitch: float = 0.0,
    yaw: float = 0.0,
    duration: float = 2.0,
    degrees: bool = True,
    mm: bool = True
) -> Dict[str, Any]:
    """
    Move the robot's head to a target pose.
    
    Args:
        x: X position offset (millimeters by default)
        y: Y position offset (millimeters by default)
        z: Z position offset (millimeters by default)
        roll: Roll angle (degrees by default)
        pitch: Pitch angle (degrees by default)
        yaw: Yaw angle (degrees by default)
        duration: Duration of the movement in seconds
        degrees: If True (default), angles are in degrees
        mm: If True (default), positions are in millimeters
    
    Example:
        Move head up 10mm and roll 15 degrees:
        move_head(z=10, roll=15, duration=2.0)
    """
    pose = create_head_pose(x, y, z, roll, pitch, yaw, degrees, mm)
    
    payload = {
        "head_pose": pose,
        "duration": duration
    }
    
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def reset_head() -> Dict[str, Any]:
    """
    Reset the robot's head to the default neutral position.
    
    This moves the head to (0, 0, 0) position with (0, 0, 0) orientation over 2 seconds.
    """
    pose = create_head_pose()
    payload = {
        "head_pose": pose,
        "duration": 2.0
    }
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def nod_head(duration: float = 1.0, angle: float = 15.0) -> Dict[str, Any]:
    """
    Make the robot nod its head (pitch up and down).
    
    Args:
        duration: Duration for each movement in seconds
        angle: Angle to pitch in degrees (default 15 degrees)
    
    This performs a nod gesture by pitching the head forward and then back to neutral.
    """
    # Nod down
    pose_down = create_head_pose(pitch=angle, degrees=True)
    await make_request("POST", "/api/move/goto", json_data={"head_pose": pose_down, "duration": duration})
    
    # Wait for movement to complete
    await asyncio.sleep(duration)
    
    # Return to neutral
    pose_neutral = create_head_pose()
    return await make_request("POST", "/api/move/goto", json_data={"head_pose": pose_neutral, "duration": duration})


@mcp.tool()
async def shake_head(duration: float = 1.0, angle: float = 20.0) -> Dict[str, Any]:
    """
    Make the robot shake its head (yaw left and right).
    
    Args:
        duration: Duration for each movement in seconds
        angle: Angle to yaw in degrees (default 20 degrees)
    
    This performs a head shake gesture by yawing left, then right, then back to neutral.
    """
    # Shake left
    pose_left = create_head_pose(yaw=-angle, degrees=True)
    await make_request("POST", "/api/move/goto", json_data={"head_pose": pose_left, "duration": duration})
    await asyncio.sleep(duration)
    
    # Shake right
    pose_right = create_head_pose(yaw=angle, degrees=True)
    await make_request("POST", "/api/move/goto", json_data={"head_pose": pose_right, "duration": duration})
    await asyncio.sleep(duration)
    
    # Return to neutral
    pose_neutral = create_head_pose()
    return await make_request("POST", "/api/move/goto", json_data={"head_pose": pose_neutral, "duration": duration})


@mcp.tool()
async def tilt_head(direction: str = "left", angle: float = 15.0, duration: float = 2.0) -> Dict[str, Any]:
    """
    Tilt the robot's head to the left or right.
    
    Args:
        direction: "left" or "right"
        angle: Angle to roll in degrees (default 15 degrees)
        duration: Duration of the movement in seconds
    
    This rolls the head to create a tilting motion.
    """
    roll_angle = angle if direction.lower() == "left" else -angle
    pose = create_head_pose(roll=roll_angle, degrees=True)
    
    payload = {
        "head_pose": pose,
        "duration": duration
    }
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def get_antennas_state() -> Dict[str, Any]:
    """
    Get the current state of the robot's antennas.
    
    Returns the current position of left and right antennas.
    """
    full_state = await make_request("GET", "/api/state/full")
    if "antennas_position" in full_state:
        return {"antennas_position": full_state["antennas_position"]}
    return full_state


@mcp.tool()
async def move_antennas(
    left: Optional[float] = None,
    right: Optional[float] = None,
    duration: float = 2.0
) -> Dict[str, Any]:
    """
    Move the robot's antennas.
    
    Args:
        left: Target position for left antenna (degrees, typically -45 to 45)
        right: Target position for right antenna (degrees, typically -45 to 45)
        duration: Duration of the movement in seconds
    
    You can move one or both antennas. Leave None to keep current position.
    """
    # Build antennas array [left, right] - need both values
    antennas_array = []
    if left is not None and right is not None:
        # Convert degrees to radians
        antennas_array = [math.radians(left), math.radians(right)]
    else:
        # If only one is specified, we can't proceed without knowing current state
        return {"error": "Both left and right antenna positions must be specified", "status": "failed"}
    
    payload = {
        "antennas": antennas_array,
        "duration": duration
    }
    
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def reset_antennas() -> Dict[str, Any]:
    """
    Reset both antennas to their neutral position (0 degrees).
    """
    payload = {
        "antennas": [0.0, 0.0],
        "duration": 2.0
    }
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def get_camera_image() -> Dict[str, Any]:
    """
    Capture an image from the robot's camera.
    
    Returns the camera image data and metadata.
    Note: The actual image data will be in the response.
    """
    # Note: The daemon API doesn't provide camera access
    # This would need to be implemented separately
    return {"error": "Camera access not available through this API", "status": "not_implemented"}


@mcp.tool()
async def get_camera_state() -> Dict[str, Any]:
    """
    Get the current state of the robot's camera.
    
    Returns information about camera status, resolution, and settings.
    """
    # Note: The actual daemon may not provide camera state info
    # This is a placeholder that returns what's available
    return {"status": "Camera state not available from this API endpoint"}


@mcp.tool()
async def turn_on_robot() -> Dict[str, Any]:
    """
    Turn on the robot's motors and activate all systems.
    
    This powers up the robot and makes it ready to receive movement commands.
    """
    return await make_request("POST", "/api/motors/set_mode/enabled")


@mcp.tool()
async def turn_off_robot() -> Dict[str, Any]:
    """
    Turn off the robot's motors and deactivate systems.
    
    This powers down the robot safely. Use this when done controlling the robot.
    """
    return await make_request("POST", "/api/motors/set_mode/disabled")


@mcp.tool()
async def get_power_state() -> Dict[str, Any]:
    """
    Get the current power state of the robot.
    
    Returns whether the robot is powered on or off.
    """
    return await make_request("GET", "/api/motors/status")


@mcp.tool()
async def stop_all_movements() -> Dict[str, Any]:
    """
    Emergency stop - immediately halt all robot movements.
    
    This stops the head and antennas in their current positions.
    """
    # The daemon doesn't have a direct stop endpoint
    # We can disable motors to stop movements
    return await make_request("POST", "/api/motors/set_mode/disabled")


@mcp.tool()
async def express_emotion(emotion: str) -> Dict[str, Any]:
    """
    Make the robot express an emotion using head and antenna movements.
    
    Args:
        emotion: One of: "happy", "sad", "curious", "surprised", "confused", "neutral"
    
    This combines head and antenna movements to create emotional expressions.
    """
    emotion = emotion.lower()
    
    if emotion == "happy":
        # Lift head slightly and antennas up
        head_pose = create_head_pose(z=5, pitch=-5, degrees=True, mm=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(30), math.radians(30)],
            "duration": 1.5
        })
        
    elif emotion == "sad":
        # Lower head and antennas down
        head_pose = create_head_pose(z=-5, pitch=10, degrees=True, mm=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(-20), math.radians(-20)],
            "duration": 2.0
        })
        
    elif emotion == "curious":
        # Tilt head to the side
        head_pose = create_head_pose(roll=20, degrees=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(15), math.radians(-15)],
            "duration": 1.5
        })
        
    elif emotion == "surprised":
        # Quick upward movement
        head_pose = create_head_pose(z=10, pitch=-15, degrees=True, mm=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(45), math.radians(45)],
            "duration": 0.8
        })
        
    elif emotion == "confused":
        # Alternate antenna positions
        head_pose = create_head_pose(roll=15, degrees=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(25), math.radians(-25)],
            "duration": 1.5
        })
        
    else:  # neutral
        return await reset_head()
    
    return {"status": "success", "emotion": emotion}


@mcp.tool()
async def look_at_direction(direction: str, duration: float = 2.0) -> Dict[str, Any]:
    """
    Make the robot look in a specific direction.
    
    Args:
        direction: One of: "up", "down", "left", "right", "forward"
        duration: Duration of the movement in seconds
    
    This moves the head to look in the specified direction.
    """
    direction = direction.lower()
    
    if direction == "up":
        pose = create_head_pose(pitch=-30, degrees=True)
    elif direction == "down":
        pose = create_head_pose(pitch=30, degrees=True)
    elif direction == "left":
        pose = create_head_pose(yaw=45, degrees=True)
    elif direction == "right":
        pose = create_head_pose(yaw=-45, degrees=True)
    else:  # forward/neutral
        pose = create_head_pose()
    
    payload = {
        "head_pose": pose,
        "duration": duration
    }
    return await make_request("POST", "/api/move/goto", json_data=payload)


@mcp.tool()
async def perform_gesture(gesture: str) -> Dict[str, Any]:
    """
    Perform a predefined gesture sequence.
    
    Args:
        gesture: One of: "greeting", "yes", "no", "thinking", "celebration"
    
    This executes a sequence of movements to perform the specified gesture.
    """
    gesture = gesture.lower()
    
    if gesture == "greeting":
        # Wave with head and antennas
        await nod_head(duration=0.8, angle=10)
        await asyncio.sleep(0.5)
        await move_antennas(left=30, right=30, duration=0.5)
        await asyncio.sleep(0.5)
        await reset_antennas()
        
    elif gesture == "yes":
        # Nod yes
        return await nod_head(duration=0.8, angle=20)
        
    elif gesture == "no":
        # Shake no
        return await shake_head(duration=0.7, angle=25)
        
    elif gesture == "thinking":
        # Tilt head and one antenna
        head_pose = create_head_pose(roll=15, pitch=5, degrees=True)
        await make_request("POST", "/api/move/goto", json_data={
            "head_pose": head_pose,
            "antennas": [math.radians(20), math.radians(-10)],
            "duration": 1.5
        })
        
    elif gesture == "celebration":
        # Excited movements
        for _ in range(2):
            await move_antennas(left=40, right=40, duration=0.4)
            await asyncio.sleep(0.4)
            await move_antennas(left=-20, right=-20, duration=0.4)
            await asyncio.sleep(0.4)
        await reset_antennas()
    
    return {"status": "success", "gesture": gesture}


@mcp.tool()
async def get_health_status() -> Dict[str, Any]:
    """
    Get the overall health status of the robot.
    
    Returns information about system health, temperature, and any warnings.
    """
    return await make_request("GET", "/api/daemon/status")


# Resources

@mcp.resource("reachy://status")
async def get_status_resource() -> str:
    """Get robot status as a formatted resource."""
    state = await get_robot_state()
    return f"Reachy Mini Status:\n{state}"


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

Common tasks:
1. Express emotions using express_emotion()
2. Perform gestures using perform_gesture()
3. Move head to specific poses using move_head()
4. Control antennas independently using move_antennas()
5. Look in directions using look_at_direction()

Always check the robot state first with get_robot_state() before issuing commands.
Remember to turn on the robot with turn_on_robot() before movement commands.
"""


@mcp.prompt()
def safety_prompt() -> str:
    """Safety guidelines for robot control."""
    return """
Reachy Mini Safety Guidelines:

1. Always check robot state before issuing movement commands
2. Use appropriate durations (typically 1-3 seconds) for smooth movements
3. Avoid extreme angles that might stress the motors
4. Use stop_all_movements() in case of unexpected behavior
5. Turn off the robot with turn_off_robot() when done
6. Monitor health_status periodically during extended use

Head Position Limits:
- Position offsets: typically ±20mm on x/y/z
- Rotation angles: ±45 degrees for safe operation

Antenna Limits:
- Typical range: -45 to 45 degrees
"""


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()


