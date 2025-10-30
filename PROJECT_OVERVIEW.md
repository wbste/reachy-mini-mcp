# Reachy Mini MCP Server - Project Overview

## What is This?

This is a **Model Context Protocol (MCP) server** that allows AI assistants like Claude to control the Reachy Mini robot. Built with [FastMCP](https://github.com/jlowin/fastmcp), it provides a natural language interface to control the robot's movements, emotions, and gestures.

## Architecture

```
┌─────────────────────┐
│   AI Assistant      │  (Claude Desktop, etc.)
│   "Make robot nod"  │
└──────────┬──────────┘
           │ MCP Protocol (stdio)
           ▼
┌─────────────────────┐
│  FastMCP Server     │  (server.py)
│  - 20+ MCP Tools    │
│  - Resources        │
│  - Prompts          │
└──────────┬──────────┘
           │ HTTP REST API
           ▼
┌─────────────────────┐
│  Reachy Daemon      │  (localhost:8000)
│  - Motor Control    │
│  - State Management │
└──────────┬──────────┘
           │ USB/WiFi/Simulation
           ▼
┌─────────────────────┐
│  Reachy Mini Robot  │
│  - Head (3-DOF)     │
│  - Antennas (2)     │
│  - Camera           │
└─────────────────────┘
```

## Project Structure

```
reachy-mini-mcp/
│
├── server.py                           # Main MCP server (FastMCP)
├── requirements.txt                    # Python dependencies
│
├── README.md                           # Full documentation
├── QUICK_START.md                      # Quick start guide (5 min setup)
├── TOOLS.md                            # Complete tools reference
├── PROJECT_OVERVIEW.md                 # This file
│
├── example_usage.py                    # Python examples
├── test_connection.py                  # Connection test utility
│
├── setup.sh                            # Setup script (macOS/Linux)
├── setup.ps1                           # Setup script (Windows)
├── start.sh                            # Quick start script
│
├── claude_desktop_config.example.json  # Claude Desktop config example
└── .gitignore                          # Git ignore rules
```

## Key Features

### 🎯 **20+ MCP Tools**

#### Movement Control (8 tools)
- `move_head()` - Precise 6-DOF head positioning
- `reset_head()` - Return to neutral
- `nod_head()` - Nod gesture
- `shake_head()` - Shake gesture
- `tilt_head()` - Tilt left/right
- `look_at_direction()` - Look up/down/left/right
- `move_antennas()` - Control antennas
- `reset_antennas()` - Reset antennas

#### Emotions (6 emotions)
- Happy, Sad, Curious, Surprised, Confused, Neutral

#### Gestures (5 gestures)
- Greeting, Yes, No, Thinking, Celebration

#### State & Monitoring (5 tools)
- `get_robot_state()` - Full state
- `get_head_state()` - Head position
- `get_antennas_state()` - Antenna positions
- `get_power_state()` - Power status
- `get_health_status()` - Health check

#### Control (4 tools)
- `turn_on_robot()` - Power on
- `turn_off_robot()` - Power off
- `stop_all_movements()` - Emergency stop
- Camera tools

### 📚 **MCP Resources**
- `reachy://status` - Robot status
- `reachy://capabilities` - Capabilities description

### 💡 **MCP Prompts**
- `control_prompt` - Control guidelines
- `safety_prompt` - Safety guidelines

## Technology Stack

- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp) (Python)
- **Robot SDK**: [Reachy Mini SDK](https://github.com/pollen-robotics/reachy_mini)
- **HTTP Client**: httpx (async)
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/)

## Quick Start

```bash
# 1. Setup (one time)
./setup.sh

# 2. Start daemon (in terminal 1)
source .venv/bin/activate
reachy-mini-daemon --sim

# 3. Test connection (in terminal 2)
source .venv/bin/activate
python test_connection.py

# 4. Start MCP server
python server.py

# Or use quick start script
./start.sh
```

## Usage Examples

### With Claude Desktop

After configuring Claude Desktop (see QUICK_START.md):

```
User: "Make the robot nod its head"
Claude: *calls nod_head() tool*

User: "Express happiness and then wave"
Claude: *calls express_emotion("happy") then perform_gesture("greeting")*

User: "Turn on the robot, look around, and show curiosity"
Claude: *calls turn_on_robot(), look_at_direction() series, express_emotion("curious")*
```

### With Python

```python
from server import move_head, express_emotion, turn_on_robot

# Turn on and express emotion
await turn_on_robot()
await express_emotion("happy")
await move_head(z=10, roll=15, duration=2.0)
```

See `example_usage.py` for complete examples.

## Use Cases

### 🎭 Entertainment & Interaction
- Greet visitors with gestures
- Express emotions during conversations
- Interactive storytelling assistant

### 📸 Photography & Content Creation
- Position robot for photos/videos
- Demonstrate emotional expressions
- Choreographed movements

### 🎓 Education & Research
- Teach robotics concepts
- Human-robot interaction studies
- AI assistant integration demos

### 🤝 Assistive Applications
- Reception desk greeter
- Meeting room companion
- Interactive display assistant

### 🎮 Gaming & Entertainment
- Tabletop game companion
- Interactive game master
- Physical avatar for virtual characters

## Development Workflow

### Adding New Tools

1. Define tool in `server.py`:
```python
@mcp.tool()
async def my_new_tool(param: str) -> Dict[str, Any]:
    """Tool description."""
    return await make_request("POST", "/api/endpoint", json_data={...})
```

2. Document in `TOOLS.md`
3. Add example to `example_usage.py`
4. Test with `test_connection.py`

### Testing

```bash
# Test daemon connection
python test_connection.py

# Run examples
python example_usage.py

# Test specific tool
python -c "import asyncio; from server import nod_head; asyncio.run(nod_head())"
```

## Safety Features

1. **Soft Limits**: Recommended ranges for safe operation
2. **Emergency Stop**: `stop_all_movements()` tool
3. **State Monitoring**: Real-time state checks
4. **Power Management**: Explicit on/off control
5. **Error Handling**: Graceful error responses

## Configuration

### Environment Variables
- `REACHY_BASE_URL`: Override default daemon URL (default: http://localhost:8000)

### Claude Desktop Config
See `claude_desktop_config.example.json` for template.

## Troubleshooting

### Common Issues

**MCP server won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt
```

**Can't connect to daemon:**
```bash
# Test connection
curl http://localhost:8000/api/state/full

# Start daemon if needed
reachy-mini-daemon --sim
```

**Robot not moving:**
1. Check if daemon is running
2. Turn on robot with `turn_on_robot()`
3. Check robot state with `get_robot_state()`

See README.md for detailed troubleshooting.

## Files Reference

| File | Purpose |
|------|---------|
| `server.py` | Main MCP server implementation |
| `requirements.txt` | Python package dependencies |
| `README.md` | Full documentation and API reference |
| `QUICK_START.md` | 5-minute getting started guide |
| `TOOLS.md` | Complete tools reference with examples |
| `example_usage.py` | Python usage examples |
| `test_connection.py` | Connection test utility |
| `setup.sh` / `setup.ps1` | Setup scripts for different OS |
| `start.sh` | Quick start launcher |
| `claude_desktop_config.example.json` | Claude Desktop config template |

## Performance

- **Tool Latency**: 50-200ms (depends on daemon response)
- **Movement Smoothness**: Configurable duration (1-3s recommended)
- **Concurrent Tools**: Safe to call sequentially
- **Resource Usage**: Minimal (< 50MB RAM)

## Limitations

1. **Sequential Movements**: Complex gestures require multiple tool calls
2. **No Direct Motor Access**: Works through daemon API
3. **Network Dependent**: Requires daemon to be running
4. **No Visual Feedback**: Camera image capture available but not real-time streaming

## Future Enhancements

Possible additions:
- [ ] Custom gesture recording/playback
- [ ] Inverse kinematics for point-at-object
- [ ] Voice control integration
- [ ] Visual servoing (camera-based positioning)
- [ ] Trajectory planning for smooth paths
- [ ] Animation sequences from files
- [ ] Multi-robot coordination

## Resources

### Documentation
- [README.md](README.md) - Full documentation
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [TOOLS.md](TOOLS.md) - Tools reference

### External Links
- [Reachy Mini GitHub](https://github.com/pollen-robotics/reachy_mini)
- [Reachy Mini Docs](https://docs.pollen-robotics.com/)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Reachy Mini Blog](https://huggingface.co/blog/reachy-mini)

### Community
- [Reachy Mini Issues](https://github.com/pollen-robotics/reachy_mini/issues)
- [Pollen Robotics](https://www.pollen-robotics.com/)
- [Hugging Face](https://huggingface.co/)

## License

This project is licensed under the Apache 2.0 License, matching the Reachy Mini SDK.

## Credits

- **Built with**: [FastMCP](https://github.com/jlowin/fastmcp) by Marvin
- **For**: [Reachy Mini](https://github.com/pollen-robotics/reachy_mini) by Pollen Robotics & Hugging Face
- **Protocol**: [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes with `test_connection.py`
4. Update documentation (TOOLS.md if adding tools)
5. Submit a pull request

## Support

- **MCP Server Issues**: Open an issue in this repository
- **Reachy Mini Issues**: [GitHub Issues](https://github.com/pollen-robotics/reachy_mini/issues)
- **FastMCP Issues**: [GitHub Issues](https://github.com/jlowin/fastmcp/issues)

---

**Version**: 1.0.0  
**Last Updated**: October 30, 2025  
**Status**: Production Ready ✅

---

**Get Started**: See [QUICK_START.md](QUICK_START.md) for setup instructions!


