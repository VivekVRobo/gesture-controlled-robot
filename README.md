# Gesture Controlled Robot

A computer-vision controlled differential-drive robot that maps simple hand gestures to motion commands.

> **Status:** software reference implementation ready for camera + serial integration. Robot-specific serial port, motor pins, motor polarity, and safety limits must be adjusted for the physical platform.

## What it does

- Uses a webcam and MediaPipe Hands to detect one hand
- Converts finger states into a small command set
- Sends compact serial commands to a microcontroller
- Stops automatically when no valid hand is detected
- Keeps vision and motor control separated for easier debugging

## Gesture map

| Gesture | Command |
|---|---|
| Open palm | Forward |
| Fist | Stop |
| Index finger only | Left |
| Index + middle | Right |
| Thumb only | Reverse |

## Architecture

```text
Webcam → MediaPipe → gesture classifier → serial command
                                      ↓
                                Arduino/MCU
                                      ↓
                                 motor driver
                                      ↓
                              differential drive
```

## Desktop setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python vision_control.py --port COM5
```

Use `--dry-run` to test gesture detection without a robot connected.

## Serial protocol

Single ASCII characters followed by newline:

- `F` forward
- `B` backward
- `L` turn left
- `R` turn right
- `S` stop

The receiver should implement a watchdog so the robot stops if commands stop arriving.

## Safety

Always test with wheels off the ground first. The firmware should default to STOP on startup, malformed data, or communications timeout.

## Roadmap

- [x] Hand landmark detection
- [x] Gesture-to-command classifier
- [x] Serial transport
- [x] Dry-run mode
- [ ] Physical robot calibration
- [ ] Speed gestures
- [ ] Obstacle-stop layer
- [ ] Demo video and measured latency
