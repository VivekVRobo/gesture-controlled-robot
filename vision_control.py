#!/usr/bin/env python3
"""Compatibility entry point for the gesture-controlled robot."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gesture_robot.app import run


if __name__ == "__main__":
    run()
