# Reachy Mini MCP - Quick Start Guide

Get up and running with the Reachy Mini MCP server in 5 minutes!

## Prerequisites

- **Python 3.10+** installed
- **git-lfs** installed (for downloading robot models)
- **Reachy Mini** (physical robot or will use simulation)

## Quick Setup (5 minutes)

### 1. Install Dependencies (2 minutes)

**macOS/Linux:**
```bash
cd /Users/ori.nachum/Git/InnovationLabs/mcps/reachy-mini-mcp
./setup.sh
```

**Windows:**
```powershell
cd C:\path\to\InnovationLabs\mcps\reachy-mini-mcp
.\setup.ps1
```

This will:
- Create a Python virtual environment
- Install all required packages
- Optionally install MuJoCo simulation support

### 2. Start the Reachy Daemon (1 minute)

Open a terminal and activate the virtual environment:

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.\.venv\Scripts\Activate.ps1
```

Then start the daemon:

**For Simulation (recommended for testing):**
```bash
reachy-mini-daemon --sim
```

**For Real Robot:**
```bash
reachy-mini-daemon
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://localhost:8000
```

### 3. Test the MCP Server (1 minute)

Open a **new terminal** window, activate the environment again, and run the example:

```bash
source .venv/bin/activate  # or .\.venv\Scripts\Activate.ps1 on Windows
python example_usage.py
```

You should see the robot moving through various gestures and emotions!

### 4. Connect to Claude Desktop (1 minute)

#### macOS:

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```bash
# Open the config file
open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "reachy-mini": {
      "command": "python",
      "args": [
        "/Users/ori.nachum/Git/InnovationLabs/mcps/reachy-mini-mcp/server.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/ori.nachum/Git/InnovationLabs/mcps/reachy-mini-mcp/.venv/lib/python3.12/site-packages"
      }
    }
  }
}
```

#### Windows:

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "reachy-mini": {
      "command": "python",
      "args": [
        "C:\\path\\to\\InnovationLabs\\mcps\\reachy-mini-mcp\\server.py"
      ]
    }
  }
}
```

**Restart Claude Desktop** after editing the config.

## First Commands to Try

Once connected in Claude Desktop, try these prompts:

### Basic Movements

> "Make the Reachy Mini robot nod its head"

> "Move the robot's head to look left"

> "Make the antennas move up"

### Emotions

> "Make the robot look happy"

> "Express curiosity with the robot"

> "Show a surprised emotion"

### Gestures

> "Make the robot wave hello"

> "Perform a thinking gesture"

> "Do a celebration gesture"

### Complex Interactions

> "Turn on the robot, make it look around, nod yes, then turn it off"

> "Express happiness and then perform a celebration"

> "Make the robot greet me and then look curious"

## Troubleshooting

### "Cannot connect to daemon"

Make sure the daemon is running:
```bash
# Check if daemon is running
curl http://localhost:8000/api/state/full
```

If not running, start it:
```bash
reachy-mini-daemon --sim
```

### "Module not found" errors

Activate the virtual environment:
```bash
source .venv/bin/activate  # macOS/Linux
# or
.\.venv\Scripts\Activate.ps1  # Windows
```

### Claude Desktop doesn't see the tools

1. Check the config file path is correct
2. Make sure paths in the config use absolute paths
3. Restart Claude Desktop completely (quit and reopen)
4. Check Claude Desktop logs (Help → Show Logs)

### Robot not moving in simulation

On macOS, MuJoCo requires `mjpython`:
```bash
# Install mujoco
pip install mujoco

# Run daemon with mjpython
mjpython -m reachy_mini.daemon.app.main --sim
```

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for Python examples
- Explore the available tools in Claude Desktop
- Try creating custom gesture sequences
- Integrate with vision or voice commands

## Common Use Cases

### Photography Assistant
```
"Turn on the robot, look up, tilt left 20 degrees, hold for 3 seconds"
```

### Meeting Greeter
```
"Perform a greeting gesture, then look at the camera and nod"
```

### Emotion Display
```
"Show happiness for 2 seconds, then surprise, then return to neutral"
```

### Interactive Demo
```
"Look around the room (left, right, up, down), express curiosity, 
then perform a thinking gesture"
```

## Need Help?

- **MCP Server Issues**: Check the README.md troubleshooting section
- **Reachy Mini Issues**: Visit [github.com/pollen-robotics/reachy_mini](https://github.com/pollen-robotics/reachy_mini)
- **FastMCP Issues**: Visit [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)

## Tips

1. **Always start the daemon first** before using the MCP server
2. **Use simulation mode** for development and testing
3. **Turn on the robot** with `turn_on_robot()` before sending movement commands
4. **Turn off the robot** with `turn_off_robot()` when done to save power
5. **Use stop_all_movements()** if something goes wrong

Enjoy controlling your Reachy Mini robot! 🤖


