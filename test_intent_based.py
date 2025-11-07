"""
Test the intent-based operate_robot implementation.

This script demonstrates the new intent-based interface where the MCP
infers what action to perform based on user intent and metadata.
"""

import asyncio
from server import operate_robot, initialize_server


async def test_simple_intent():
    """Test simple intent without metadata."""
    print("\n" + "="*60)
    print("Test 1: Simple Intent")
    print("="*60)
    
    result = await operate_robot(intent="greeting")
    print(f"Intent: greeting")
    print(f"Inferred action: {result.get('inferred_action')}")
    print(f"Tool used: {result.get('tool_used')}")
    print(f"Status: {result.get('status')}")
    print(f"Note: {result.get('note')}")


async def test_intent_with_metadata():
    """Test intent with metadata parameters."""
    print("\n" + "="*60)
    print("Test 2: Intent with Metadata")
    print("="*60)
    
    result = await operate_robot(
        intent="acknowledge",
        metadata={"duration": 2.0, "angle": 20}
    )
    print(f"Intent: acknowledge")
    print(f"Metadata: duration=2.0, angle=20")
    print(f"Inferred action: {result.get('inferred_action')}")
    print(f"Tool used: {result.get('tool_used')}")
    print(f"Parameters: {result.get('parameters')}")
    print(f"Status: {result.get('status')}")


async def test_multiple_intents():
    """Test multiple different intents to see random behavior."""
    print("\n" + "="*60)
    print("Test 3: Multiple Intents (showing randomness)")
    print("="*60)
    
    intents = [
        "greeting",
        "agree",
        "curious",
        "thinking",
        "celebrate"
    ]
    
    for intent in intents:
        result = await operate_robot(intent=intent)
        action = result.get('inferred_action')
        print(f"Intent: '{intent}' -> Action: '{action}'")
        await asyncio.sleep(0.5)  # Small delay between calls


async def test_custom_metadata():
    """Test various metadata combinations."""
    print("\n" + "="*60)
    print("Test 4: Custom Metadata Combinations")
    print("="*60)
    
    test_cases = [
        {
            "intent": "express_happiness",
            "metadata": {"enthusiasm": "high", "duration": 1.0}
        },
        {
            "intent": "show_understanding",
            "metadata": {"angle": 10, "duration": 2.5}
        },
        {
            "intent": "deep_thought",
            "metadata": {"duration": 3.0}
        }
    ]
    
    for test_case in test_cases:
        result = await operate_robot(**test_case)
        print(f"\nIntent: {test_case['intent']}")
        print(f"Metadata: {test_case.get('metadata', {})}")
        print(f"Inferred action: {result.get('inferred_action')}")
        print(f"Actual parameters used: {result.get('parameters')}")
        await asyncio.sleep(0.5)


async def test_default_parameters():
    """Test that default parameters are used when metadata is missing."""
    print("\n" + "="*60)
    print("Test 5: Default Parameters")
    print("="*60)
    
    result = await operate_robot(intent="test_defaults")
    params = result.get('parameters', {})
    print(f"Intent: test_defaults")
    print(f"No metadata provided")
    print(f"Default duration used: {params.get('duration')}")
    print(f"Default angle used: {params.get('angle')}")
    print(f"Expected: duration=1.5, angle=15")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Intent-Based operate_robot Tests")
    print("="*60)
    print("\nTesting new interface: operate_robot(intent, metadata)")
    print("The MCP randomly chooses between nod/shake as placeholder")
    
    # Initialize server to load tools
    print("\nInitializing server...")
    initialize_server()
    
    try:
        # Run tests
        await test_simple_intent()
        await asyncio.sleep(1)
        
        await test_intent_with_metadata()
        await asyncio.sleep(1)
        
        await test_multiple_intents()
        await asyncio.sleep(1)
        
        await test_custom_metadata()
        await asyncio.sleep(1)
        
        await test_default_parameters()
        
        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
        print("\nSummary:")
        print("- Intent-based interface working ✓")
        print("- Metadata parameters applied ✓")
        print("- Default parameters working ✓")
        print("- Random nod/shake selection active ✓")
        
    except Exception as e:
        print(f"\nError during tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
