# Reachy Mini MCP Tools Reference

Complete reference of all available MCP tools for controlling Reachy Mini.

## Tool Categories

- [State & Monitoring](#state--monitoring)
- [Power Management](#power-management)
- [Head Control](#head-control)
- [Antenna Control](#antenna-control)
- [Emotions & Gestures](#emotions--gestures)
- [Camera](#camera)
- [Safety](#safety)

---

## State & Monitoring

### `get_robot_state()`
Get the complete state of the Reachy Mini robot.

**Parameters:** None

**Returns:** 
```json
{
  "head": { "x": 0, "y": 0, "z": 0, "roll": 0, "pitch": 0, "yaw": 0 },
  "antennas": { "left": 0, "right": 0 },
  "power": "on",
  "camera": { "status": "ready" },
  ...
}
```

**Example Usage:**
```
"What is the current state of the robot?"
"Show me the robot's status"
```

---

### `get_head_state()`
Get the current state of the robot's head.

**Parameters:** None

**Returns:** 
```json
{
  "x": 0.0, "y": 0.0, "z": 0.0,
  "roll": 0.0, "pitch": 0.0, "yaw": 0.0
}
```

**Example Usage:**
```
"What is the head position?"
"Where is the head currently pointing?"
```

---

### `get_antennas_state()`
Get the current state of the antennas.

**Parameters:** None

**Returns:**
```json
{
  "left": 0.0,
  "right": 0.0
}
```

**Example Usage:**
```
"What are the antenna positions?"
"Show me the current antenna angles"
```

---

### `get_health_status()`
Get the overall health status of the robot.

**Parameters:** None

**Returns:** System health information including temperature, warnings, etc.

**Example Usage:**
```
"Is the robot healthy?"
"Check the robot's health"
```

---

## Power Management

### `turn_on_robot()`
Power on the robot's motors and systems.

**Parameters:** None

**Returns:** Success/failure status

**Example Usage:**
```
"Turn on the robot"
"Power up the robot"
"Activate the robot"
```

**⚠️ Important:** Always turn on the robot before issuing movement commands.

---

### `turn_off_robot()`
Power off the robot's motors and systems.

**Parameters:** None

**Returns:** Success/failure status

**Example Usage:**
```
"Turn off the robot"
"Power down the robot"
"Deactivate the robot"
```

---

### `get_power_state()`
Check if the robot is powered on or off.

**Parameters:** None

**Returns:**
```json
{
  "powered": true
}
```

**Example Usage:**
```
"Is the robot on?"
"What's the power state?"
```

---

## Head Control

### `move_head(x, y, z, roll, pitch, yaw, duration, degrees, mm)`
Move the robot's head to a specific pose.

**Parameters:**
- `x` (float, optional): X position offset (mm by default), default: 0.0
- `y` (float, optional): Y position offset (mm by default), default: 0.0
- `z` (float, optional): Z position offset (mm by default), default: 0.0
- `roll` (float, optional): Roll angle (degrees by default), default: 0.0
- `pitch` (float, optional): Pitch angle (degrees by default), default: 0.0
- `yaw` (float, optional): Yaw angle (degrees by default), default: 0.0
- `duration` (float, optional): Duration in seconds, default: 2.0
- `degrees` (bool, optional): Use degrees for angles, default: True
- `mm` (bool, optional): Use millimeters for positions, default: True

**Example Usage:**
```
"Move the head up 10mm"
"Tilt the head 15 degrees to the right"
"Move head to x=5, y=0, z=10, roll=15 over 2 seconds"
```

**Safe Ranges:**
- Position: ±20mm
- Rotation: ±45 degrees

---

### `reset_head()`
Reset the head to neutral position (0, 0, 0).

**Parameters:** None

**Example Usage:**
```
"Reset the head"
"Return head to neutral position"
"Center the head"
```

---

### `nod_head(duration, angle)`
Make the robot nod its head (pitch forward and back).

**Parameters:**
- `duration` (float, optional): Duration of each movement, default: 1.0
- `angle` (float, optional): Nod angle in degrees, default: 15.0

**Example Usage:**
```
"Nod the head"
"Make the robot nod yes"
"Nod with a 20 degree angle"
```

---

### `shake_head(duration, angle)`
Make the robot shake its head (yaw left and right).

**Parameters:**
- `duration` (float, optional): Duration of each movement, default: 1.0
- `angle` (float, optional): Shake angle in degrees, default: 20.0

**Example Usage:**
```
"Shake the head"
"Make the robot shake its head no"
"Shake head with 25 degree angle"
```

---

### `tilt_head(direction, angle, duration)`
Tilt the robot's head to the left or right.

**Parameters:**
- `direction` (str): "left" or "right"
- `angle` (float, optional): Tilt angle in degrees, default: 15.0
- `duration` (float, optional): Movement duration, default: 2.0

**Example Usage:**
```
"Tilt head to the left"
"Tilt head right 20 degrees"
```

---

### `look_at_direction(direction, duration)`
Make the robot look in a specific direction.

**Parameters:**
- `direction` (str): "up", "down", "left", "right", or "forward"
- `duration` (float, optional): Movement duration, default: 2.0

**Example Usage:**
```
"Look up"
"Look to the left"
"Look forward"
"Look down for 1 second"
```

---

## Antenna Control

### `move_antennas(left, right, duration)`
Move the robot's antennas independently.

**Parameters:**
- `left` (float, optional): Left antenna position in degrees (-45 to 45)
- `right` (float, optional): Right antenna position in degrees (-45 to 45)
- `duration` (float, optional): Movement duration, default: 2.0

**Example Usage:**
```
"Move left antenna to 30 degrees"
"Move both antennas up"
"Set left antenna to 40 and right to -40"
```

**Note:** You can specify one or both antennas. Unspecified antennas remain at current position.

---

### `reset_antennas()`
Reset both antennas to neutral position (0 degrees).

**Parameters:** None

**Example Usage:**
```
"Reset the antennas"
"Put antennas back to neutral"
"Center the antennas"
```

---

## Emotions & Gestures

### `express_emotion(emotion)`
Make the robot express an emotion using head and antenna movements.

**Parameters:**
- `emotion` (str): One of: "happy", "sad", "curious", "surprised", "confused", "neutral"

**Emotion Descriptions:**
- **happy**: Head up slightly, antennas raised
- **sad**: Head down, antennas lowered
- **curious**: Head tilted, asymmetric antennas
- **surprised**: Quick upward movement, antennas fully raised
- **confused**: Head tilted, alternating antenna positions
- **neutral**: Return to default position

**Example Usage:**
```
"Express happiness"
"Make the robot look sad"
"Show curiosity"
"Be surprised"
```

---

### `perform_gesture(gesture)`
Perform a predefined gesture sequence.

**Parameters:**
- `gesture` (str): One of: "greeting", "yes", "no", "thinking", "celebration"

**Gesture Descriptions:**
- **greeting**: Wave with head and antennas
- **yes**: Nod affirmatively
- **no**: Shake head side to side
- **thinking**: Tilt head with one antenna raised (contemplative)
- **celebration**: Excited antenna movements

**Example Usage:**
```
"Wave hello"
"Perform a greeting"
"Say yes with a gesture"
"Do a celebration"
"Show you're thinking"
```

---

## Camera

### `get_camera_image()`
Capture an image from the robot's camera.

**Parameters:** None

**Returns:** Camera image data and metadata

**Example Usage:**
```
"Take a picture"
"Capture an image"
"Show me what the robot sees"
```

---

### `get_camera_state()`
Get the current state of the camera.

**Parameters:** None

**Returns:** Camera status, resolution, and settings

**Example Usage:**
```
"What's the camera status?"
"Is the camera working?"
```

---

## Safety

### `stop_all_movements()`
**EMERGENCY STOP** - Immediately halt all robot movements.

**Parameters:** None

**Returns:** Success/failure status

**Example Usage:**
```
"Stop!"
"Emergency stop"
"Halt all movements"
```

**⚠️ Important:** Use this if the robot behaves unexpectedly or you need to stop it immediately.

---

## Combining Tools

### Example Sequences

**Greeting Sequence:**
```
1. turn_on_robot()
2. perform_gesture("greeting")
3. express_emotion("happy")
4. turn_off_robot()
```

**Look Around:**
```
1. turn_on_robot()
2. look_at_direction("left")
3. look_at_direction("right")
4. look_at_direction("up")
5. look_at_direction("forward")
6. turn_off_robot()
```

**Express Curiosity:**
```
1. turn_on_robot()
2. tilt_head("left", angle=20)
3. move_antennas(left=15, right=-15)
4. reset_head()
5. turn_off_robot()
```

---

## Tips & Best Practices

1. **Always turn on first**: Use `turn_on_robot()` before movement commands
2. **Use appropriate durations**: 1-3 seconds for smooth movements
3. **Stay within limits**: ±20mm for position, ±45° for rotation
4. **Turn off when done**: Use `turn_off_robot()` to save power
5. **Monitor state**: Check `get_robot_state()` periodically
6. **Emergency stop**: Use `stop_all_movements()` if needed

---

## Error Handling

If a tool fails, check:
1. Is the daemon running? (`http://localhost:8000`)
2. Is the robot powered on? Use `get_power_state()`
3. Are parameters within safe limits?
4. Is there an active movement in progress?

---

## Resources & Prompts

The MCP server also provides:

### Resources
- `reachy://status` - Formatted robot status
- `reachy://capabilities` - Robot capabilities description

### Prompts
- `control_prompt` - Control guidelines
- `safety_prompt` - Safety guidelines and limits

---

## Quick Reference Table

| Category | Tool | Quick Description |
|----------|------|-------------------|
| State | `get_robot_state()` | Get full state |
| State | `get_head_state()` | Get head position |
| State | `get_antennas_state()` | Get antenna positions |
| Power | `turn_on_robot()` | Power on |
| Power | `turn_off_robot()` | Power off |
| Head | `move_head(...)` | Move to pose |
| Head | `reset_head()` | Reset to neutral |
| Head | `nod_head(...)` | Nod yes |
| Head | `shake_head(...)` | Shake no |
| Head | `look_at_direction(...)` | Look in direction |
| Antennas | `move_antennas(...)` | Move antennas |
| Antennas | `reset_antennas()` | Reset antennas |
| Emotion | `express_emotion(...)` | Show emotion |
| Gesture | `perform_gesture(...)` | Perform gesture |
| Camera | `get_camera_image()` | Capture image |
| Safety | `stop_all_movements()` | Emergency stop |

---

## Support

For detailed documentation, see:
- [README.md](README.md) - Full documentation
- [QUICK_START.md](QUICK_START.md) - Getting started guide
- [example_usage.py](example_usage.py) - Python examples


