"""
Example usage of the Reachy Mini MCP Server tools.

This file demonstrates how to use various tools programmatically.
When using with an MCP client like Claude Desktop, you can simply
describe what you want and the AI will call these tools for you.
"""

import asyncio
from server import (
    get_robot_state,
    turn_on_robot,
    turn_off_robot,
    move_head,
    reset_head,
    nod_head,
    shake_head,
    move_antennas,
    express_emotion,
    perform_gesture,
    look_at_direction,
    get_camera_image,
)


async def example_basic_movement():
    """Example: Basic head movement."""
    print("\n=== Example: Basic Head Movement ===")
    
    # Turn on the robot
    print("Turning on robot...")
    await turn_on_robot()
    await asyncio.sleep(1)
    
    # Move head up and tilt
    print("Moving head up and tilting...")
    await move_head(z=10, roll=15, duration=2.0)
    await asyncio.sleep(2.5)
    
    # Reset to neutral
    print("Resetting to neutral position...")
    await reset_head()
    await asyncio.sleep(2.5)
    
    # Turn off
    print("Turning off robot...")
    await turn_off_robot()


async def example_emotions():
    """Example: Express different emotions."""
    print("\n=== Example: Expressing Emotions ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    emotions = ["happy", "curious", "surprised", "sad", "neutral"]
    
    for emotion in emotions:
        print(f"Expressing emotion: {emotion}")
        await express_emotion(emotion)
        await asyncio.sleep(2.5)
    
    await turn_off_robot()


async def example_gestures():
    """Example: Perform various gestures."""
    print("\n=== Example: Performing Gestures ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    gestures = ["greeting", "yes", "no", "thinking", "celebration"]
    
    for gesture in gestures:
        print(f"Performing gesture: {gesture}")
        await perform_gesture(gesture)
        await asyncio.sleep(3)
    
    await turn_off_robot()


async def example_look_around():
    """Example: Look in different directions."""
    print("\n=== Example: Looking Around ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    directions = ["left", "right", "up", "down", "forward"]
    
    for direction in directions:
        print(f"Looking {direction}...")
        await look_at_direction(direction, duration=1.5)
        await asyncio.sleep(2)
    
    await turn_off_robot()


async def example_antenna_control():
    """Example: Control antennas."""
    print("\n=== Example: Antenna Control ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    # Both antennas up
    print("Moving antennas up...")
    await move_antennas(left=30, right=30, duration=1.5)
    await asyncio.sleep(2)
    
    # Asymmetric positions
    print("Moving antennas asymmetrically...")
    await move_antennas(left=40, right=-40, duration=1.5)
    await asyncio.sleep(2)
    
    # Both antennas down
    print("Moving antennas down...")
    await move_antennas(left=-30, right=-30, duration=1.5)
    await asyncio.sleep(2)
    
    # Reset
    print("Resetting antennas...")
    await move_antennas(left=0, right=0, duration=1.5)
    await asyncio.sleep(2)
    
    await turn_off_robot()


async def example_complex_sequence():
    """Example: Complex interaction sequence."""
    print("\n=== Example: Complex Sequence ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    # Greeting sequence
    print("Performing greeting...")
    await perform_gesture("greeting")
    await asyncio.sleep(3)
    
    # Look around
    print("Looking around...")
    await look_at_direction("left", duration=1.0)
    await asyncio.sleep(1.5)
    await look_at_direction("right", duration=1.0)
    await asyncio.sleep(1.5)
    await look_at_direction("forward", duration=1.0)
    await asyncio.sleep(1.5)
    
    # Express curiosity
    print("Expressing curiosity...")
    await express_emotion("curious")
    await asyncio.sleep(2.5)
    
    # Nod yes
    print("Nodding yes...")
    await perform_gesture("yes")
    await asyncio.sleep(2)
    
    # Express happiness
    print("Expressing happiness...")
    await express_emotion("happy")
    await asyncio.sleep(2.5)
    
    # Celebrate
    print("Celebrating...")
    await perform_gesture("celebration")
    await asyncio.sleep(4)
    
    # Return to neutral
    print("Returning to neutral...")
    await reset_head()
    await asyncio.sleep(2)
    
    await turn_off_robot()


async def example_monitoring():
    """Example: Monitor robot state."""
    print("\n=== Example: Robot State Monitoring ===")
    
    # Get full robot state
    state = await get_robot_state()
    print(f"Robot State: {state}")
    
    # Note: You can parse the state to get specific information
    # about motors, positions, power status, etc.


async def example_camera():
    """Example: Capture camera image."""
    print("\n=== Example: Camera Capture ===")
    
    await turn_on_robot()
    await asyncio.sleep(1)
    
    print("Capturing image from camera...")
    image_data = await get_camera_image()
    print(f"Image captured: {image_data}")
    
    await turn_off_robot()


async def main():
    """Run all examples."""
    print("🤖 Reachy Mini MCP Server - Usage Examples")
    print("==========================================")
    print("\nMake sure the Reachy Mini daemon is running!")
    print("Start it with: reachy-mini-daemon --sim")
    print("\nPress Ctrl+C to stop\n")
    
    # Wait a bit to give user time to read
    await asyncio.sleep(3)
    
    try:
        # Run examples one by one
        # Comment out examples you don't want to run
        
        await example_basic_movement()
        await asyncio.sleep(2)
        
        await example_emotions()
        await asyncio.sleep(2)
        
        await example_gestures()
        await asyncio.sleep(2)
        
        await example_look_around()
        await asyncio.sleep(2)
        
        await example_antenna_control()
        await asyncio.sleep(2)
        
        await example_monitoring()
        await asyncio.sleep(2)
        
        # Complex sequence - uncomment to run
        # await example_complex_sequence()
        
        print("\n✅ All examples completed!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())


