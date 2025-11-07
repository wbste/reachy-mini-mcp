#!/usr/bin/env python3
"""
Test the simplified operate_robot interface.
"""
import asyncio
from server import operate_robot, initialize_server


async def test_simplified_interface():
    """Test the simplified bodyPart-based interface."""
    
    print("=" * 60)
    print("Testing Simplified operate_robot Interface")
    print("=" * 60)
    
    # Test 1: Move head
    print("\n1. Testing head movement:")
    result = await operate_robot(commands=[
        {"bodyPart": "head", "z": 10, "duration": 2.0}
    ])
    print(f"Result: {result}")
    
    # Test 2: Express emotion
    print("\n2. Testing emotion expression:")
    result = await operate_robot(commands=[
        {"bodyPart": "emotion", "emotion": "happy"}
    ])
    print(f"Result: {result}")
    
    # Test 3: Perform gesture
    print("\n3. Testing gesture:")
    result = await operate_robot(commands=[
        {"bodyPart": "gesture", "gesture": "greeting"}
    ])
    print(f"Result: {result}")
    
    # Test 4: Control antennas
    print("\n4. Testing antenna control:")
    result = await operate_robot(commands=[
        {"bodyPart": "antennas", "left": 30, "right": -30, "duration": 1.5}
    ])
    print(f"Result: {result}")
    
    # Test 5: Nod head
    print("\n5. Testing nod:")
    result = await operate_robot(commands=[
        {"bodyPart": "nod", "angle": 15, "duration": 1.0}
    ])
    print(f"Result: {result}")
    
    # Test 6: Look in direction
    print("\n6. Testing look direction:")
    result = await operate_robot(commands=[
        {"bodyPart": "look", "direction": "left", "duration": 1.0}
    ])
    print(f"Result: {result}")
    
    # Test 7: Sequence of commands
    print("\n7. Testing command sequence:")
    result = await operate_robot(commands=[
        {"bodyPart": "gesture", "gesture": "greeting"},
        {"bodyPart": "nod", "angle": 15, "duration": 2.0},
        {"bodyPart": "antennas", "left": 30, "right": -30, "duration": 1.5},
        {"bodyPart": "emotion", "emotion": "happy"}
    ])
    print(f"Result: {result}")
    
    # Test 8: Get robot state
    print("\n8. Testing state retrieval:")
    result = await operate_robot(commands=[
        {"bodyPart": "state"}
    ])
    print(f"Result: {result}")
    
    # Test 9: Power control
    print("\n9. Testing power control:")
    result = await operate_robot(commands=[
        {"bodyPart": "power", "state": "on"}
    ])
    print(f"Result: {result}")
    
    # Test 10: Error handling - missing bodyPart
    print("\n10. Testing error handling (missing bodyPart):")
    result = await operate_robot(commands=[
        {"z": 10, "duration": 2.0}
    ])
    print(f"Result: {result}")
    
    # Test 11: Error handling - unknown bodyPart
    print("\n11. Testing error handling (unknown bodyPart):")
    result = await operate_robot(commands=[
        {"bodyPart": "unknown_part", "value": 10}
    ])
    print(f"Result: {result}")
    
    # Test 12: Error handling - invalid commands type
    print("\n12. Testing error handling (invalid commands type):")
    result = await operate_robot(commands="not a list")
    print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Initialize server to load tools
    initialize_server()
    
    # Run tests
    asyncio.run(test_simplified_interface())
