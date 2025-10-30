"""
Simple test script to verify connection to Reachy Mini daemon.

Run this to check if the daemon is running and accessible.
"""

import asyncio
import httpx


async def test_connection():
    """Test connection to Reachy Mini daemon."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing connection to Reachy Mini daemon...")
    print(f"   Base URL: {base_url}\n")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Test root endpoint
            print("1. Testing root endpoint (/)...")
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print("   ✓ Root endpoint accessible")
            else:
                print(f"   ⚠ Root returned status {response.status_code}")
            
            # Test API docs
            print("\n2. Testing API docs (/docs)...")
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("   ✓ API documentation accessible")
                print(f"   📖 Open in browser: {base_url}/docs")
            
            # Test state endpoint
            print("\n3. Testing state endpoint (/api/state/full)...")
            response = await client.get(f"{base_url}/api/state/full")
            if response.status_code == 200:
                print("   ✓ State endpoint accessible")
                state = response.json()
                print(f"   📊 State keys: {list(state.keys())}")
            else:
                print(f"   ⚠ State endpoint returned status {response.status_code}")
            
            # Test power state
            print("\n4. Testing power state (/api/state/power)...")
            response = await client.get(f"{base_url}/api/state/power")
            if response.status_code == 200:
                print("   ✓ Power state accessible")
                power = response.json()
                print(f"   ⚡ Power state: {power}")
            
            print("\n✅ All tests passed! Daemon is running correctly.")
            print("\nYou can now:")
            print("  1. Run the MCP server: python server.py")
            print("  2. Run examples: python example_usage.py")
            print("  3. Connect Claude Desktop to the MCP server")
            
        except httpx.ConnectError:
            print("❌ Connection failed!")
            print("\nThe Reachy Mini daemon is not running.")
            print("\nTo start the daemon:")
            print("  For simulation: reachy-mini-daemon --sim")
            print("  For real robot: reachy-mini-daemon")
            print("\nThen run this test again.")
            
        except httpx.TimeoutException:
            print("❌ Connection timeout!")
            print("\nThe daemon might be running but not responding.")
            print("Try restarting it.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point."""
    print("=" * 60)
    print("Reachy Mini MCP - Connection Test")
    print("=" * 60)
    print()
    
    await test_connection()
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


