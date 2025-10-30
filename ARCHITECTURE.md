# Reachy Mini MCP Server - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI Assistant Layer                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │ Claude Desktop │  │ Custom Clients │  │   CLI Tools    │        │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘        │
│           │                   │                   │                 │
│           └───────────────────┼───────────────────┘                 │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                        stdio (MCP Protocol)
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                    MCP Server Layer (FastMCP)                        │
│                                │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                         server.py                             │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │                    MCP Tools (20+)                    │   │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │   │  │
│  │  │  │   Movement   │  │   Emotions   │  │  Monitoring│ │   │  │
│  │  │  │   - move_head│  │   - happy    │  │  - state   │ │   │  │
│  │  │  │   - antennas │  │   - curious  │  │  - health  │ │   │  │
│  │  │  │   - gestures │  │   - sad      │  │  - camera  │ │   │  │
│  │  │  └──────────────┘  └──────────────┘  └────────────┘ │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │                  Helper Functions                     │   │  │
│  │  │   - create_head_pose()                               │   │  │
│  │  │   - make_request()                                   │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │              MCP Resources & Prompts                  │   │  │
│  │  │   - reachy://status                                  │   │  │
│  │  │   - reachy://capabilities                            │   │  │
│  │  │   - control_prompt                                   │   │  │
│  │  │   - safety_prompt                                    │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                    HTTP REST API (httpx async)
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                    Reachy Mini Daemon Layer                          │
│                                │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │          Reachy Mini Daemon (localhost:8000)                  │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │                  FastAPI Endpoints                    │   │  │
│  │  │   GET  /api/state/full                               │   │  │
│  │  │   GET  /api/state/head                               │   │  │
│  │  │   POST /api/goto                                     │   │  │
│  │  │   POST /api/power/on                                 │   │  │
│  │  │   POST /api/power/off                                │   │  │
│  │  │   GET  /api/camera/image                             │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────┐   │  │
│  │  │                  Motor Controllers                    │   │  │
│  │  │   - Head motors (neck_roll, neck_pitch, neck_yaw)   │   │  │
│  │  │   - Antenna motors (left, right)                     │   │  │
│  │  └──────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
              USB / WiFi / Simulation (MuJoCo)
                                │
┌───────────────────────────────┼─────────────────────────────────────┐
│                       Hardware/Simulation Layer                      │
│                                │                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Reachy Mini Robot                        │  │
│  │                                                               │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  │
│  │  │     Head     │  │   Antennas   │  │    Camera    │      │  │
│  │  │   3-DOF      │  │   2 motors   │  │   Vision     │      │  │
│  │  │ (R, P, Y)    │  │ (L, R)       │  │   Sensor     │      │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │  │
│  │                                                               │  │
│  │                    OR MuJoCo Simulation                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Example: "Make the robot nod"

```
1. User Input
   │
   ▼
┌─────────────────────┐
│  Claude Desktop     │  "Make the robot nod"
└──────────┬──────────┘
           │
           │ MCP Request: call_tool("nod_head", {duration: 1.0})
           ▼
┌─────────────────────┐
│  FastMCP Server     │  @mcp.tool() async def nod_head(...)
│  (server.py)        │
└──────────┬──────────┘
           │
           │ 1. HTTP POST /api/goto {head: {pitch: 15°}}
           │ 2. await asyncio.sleep(1.0)
           │ 3. HTTP POST /api/goto {head: {pitch: 0°}}
           ▼
┌─────────────────────┐
│  Reachy Daemon      │  Receives goto commands
│  (localhost:8000)   │
└──────────┬──────────┘
           │
           │ Motor commands
           ▼
┌─────────────────────┐
│  Reachy Mini Robot  │  Executes pitch movements
└─────────────────────┘
           │
           │ Position feedback
           ▼
┌─────────────────────┐
│  Response Chain     │  Success → MCP Result → Claude
└─────────────────────┘
```

## Component Responsibilities

### MCP Server (`server.py`)

**Responsibilities:**
- Expose MCP tools for robot control
- Translate high-level commands to daemon API calls
- Manage async operations and timing
- Provide resources and prompts
- Error handling and validation

**Key Features:**
- 20+ MCP tools
- Async/await pattern for smooth movements
- Helper functions for pose creation
- Comprehensive error handling

### Reachy Daemon

**Responsibilities:**
- Direct motor control and communication
- State management and monitoring
- Camera interface
- Power management
- Real-time feedback

**Key Features:**
- FastAPI REST API
- Real-time motor control
- WebSocket support (future)
- Dashboard UI

### Robot Hardware/Simulation

**Responsibilities:**
- Execute motor commands
- Provide sensor feedback
- Physical/simulated movement
- Camera capture

**Key Features:**
- 3-DOF head (roll, pitch, yaw)
- 2 independent antennas
- Camera sensor
- MuJoCo simulation support

## Communication Protocols

### MCP Protocol (stdio)

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "move_head",
    "arguments": {
      "z": 10,
      "roll": 15,
      "duration": 2.0
    }
  }
}
```

### HTTP REST API

```http
POST /api/goto HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "head": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.01,
    "roll": 0.26,
    "pitch": 0.0,
    "yaw": 0.0
  },
  "duration": 2.0
}
```

## Tool Categories & Organization

```
MCP Tools (20+)
│
├── State & Monitoring
│   ├── get_robot_state()
│   ├── get_head_state()
│   ├── get_antennas_state()
│   ├── get_camera_state()
│   ├── get_power_state()
│   └── get_health_status()
│
├── Power Management
│   ├── turn_on_robot()
│   └── turn_off_robot()
│
├── Head Control
│   ├── move_head()
│   ├── reset_head()
│   ├── nod_head()
│   ├── shake_head()
│   ├── tilt_head()
│   └── look_at_direction()
│
├── Antenna Control
│   ├── move_antennas()
│   └── reset_antennas()
│
├── Emotions & Gestures
│   ├── express_emotion()
│   └── perform_gesture()
│
├── Camera
│   ├── get_camera_image()
│   └── get_camera_state()
│
└── Safety
    └── stop_all_movements()
```

## Deployment Models

### Model 1: Lite (USB)

```
Computer (MCP Server + Daemon) ←→ USB ←→ Robot Hardware
```

### Model 2: Wireless

```
Computer (MCP Server) ←→ WiFi ←→ Raspberry Pi (Daemon) ←→ Robot Hardware
```

### Model 3: Simulation

```
Computer (MCP Server + Daemon + MuJoCo) ←→ Simulated Robot
```

## Error Handling Flow

```
Tool Call
   │
   ▼
┌─────────────────────┐
│  Validate Params    │  Check ranges, types
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Make HTTP Request  │  Try httpx request
└──────────┬──────────┘
           │
           ├─ Success → Return result
           │
           └─ Error → Catch & return error dict
                {
                  "error": "Connection failed",
                  "status": "failed"
                }
```

## Security Considerations

1. **Local Only**: Default daemon runs on localhost only
2. **No Authentication**: Assumes trusted local environment
3. **Rate Limiting**: None (consider adding for production)
4. **Input Validation**: Parameter ranges validated
5. **Network Exposure**: Use `--no-localhost-only` with caution

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Tool Call | 50-200ms | Network + daemon processing |
| Head Movement | 1-3s | Configurable duration |
| Antenna Movement | 1-2s | Typically faster than head |
| State Query | 20-50ms | Simple GET request |
| Camera Capture | 100-300ms | Depends on resolution |
| Emergency Stop | < 50ms | High priority |

## Scalability

**Current Design:**
- Single robot per daemon instance
- Sequential tool execution
- Synchronous movements with async waits

**Future Enhancements:**
- Multi-robot coordination
- Parallel movements
- Command queuing
- Event-driven updates

## Dependencies

```
Runtime Dependencies:
├── Python 3.10+
├── fastmcp
├── httpx
├── reachy-mini SDK
└── asyncio (stdlib)

Optional Dependencies:
├── mujoco (simulation)
└── reachy-mini[dev] (development)

System Dependencies:
└── git-lfs (for model downloads)
```

## Configuration Options

**Environment Variables:**
```bash
REACHY_BASE_URL=http://localhost:8000  # Daemon URL
PYTHONPATH=...                         # Virtual env path
```

**Daemon Options:**
```bash
--sim                 # Simulation mode
--no-localhost-only   # Accept network connections
--scene <empty|minimal>  # Simulation scene
-p <port>            # Serial port (for USB)
```

## Testing Strategy

1. **Unit Tests**: Individual tool functions (future)
2. **Integration Tests**: Full daemon + MCP server
3. **Connection Tests**: `test_connection.py`
4. **Example Tests**: `example_usage.py`
5. **Manual Tests**: Claude Desktop interaction

## Monitoring & Debugging

**Daemon Logs:**
- Console output from daemon
- Dashboard at http://localhost:8000

**MCP Server Logs:**
- stdout/stderr from server.py
- Claude Desktop MCP logs (Help → Show Logs)

**Debug Tools:**
- `test_connection.py` - Connection verification
- `get_robot_state()` - State inspection
- Dashboard UI - Visual monitoring

## Extension Points

1. **New Tools**: Add `@mcp.tool()` decorated functions
2. **New Resources**: Add `@mcp.resource()` endpoints
3. **New Prompts**: Add `@mcp.prompt()` templates
4. **Custom Gestures**: Extend `perform_gesture()`
5. **Custom Emotions**: Extend `express_emotion()`

---

**Last Updated**: October 30, 2025  
**Architecture Version**: 1.0.0


