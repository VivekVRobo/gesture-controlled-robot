#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path

from gesture_robot.gestures import Command, command_from_extended_count, count_extended_fingers
from gesture_robot.stabilizer import CommandStabilizer


@dataclass
class Point:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


@dataclass
class Hand:
    landmark: list[Point]


def rotate(point: Point, angle_deg: float) -> Point:
    angle = math.radians(angle_deg)
    c, s = math.cos(angle), math.sin(angle)
    return Point(point.x * c - point.y * s, point.x * s + point.y * c, point.z)


def synthetic_hand(extended_count: int, rotation_deg: float) -> Hand:
    if not 0 <= extended_count <= 4:
        raise ValueError("extended_count must be between 0 and 4")
    points = [Point() for _ in range(21)]
    points[0] = Point(0.0, 0.0, 0.0)
    joints = ((5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20))
    x_positions = (-0.30, -0.10, 0.10, 0.30)
    for index, ((mcp_id, pip_id, tip_id), x) in enumerate(zip(joints, x_positions)):
        mcp = Point(x, -0.30)
        pip = Point(x, -0.60)
        tip = Point(x, -1.00) if index < extended_count else Point(x, -0.34)
        points[mcp_id] = rotate(mcp, rotation_deg)
        points[pip_id] = rotate(pip, rotation_deg)
        points[tip_id] = rotate(tip, rotation_deg)
    return Hand(points)


def geometry_cases() -> list[dict]:
    cases: list[dict] = []
    for extended_count in range(5):
        expected_command = command_from_extended_count(extended_count)
        for rotation_deg in range(0, 360, 15):
            hand = synthetic_hand(extended_count, float(rotation_deg))
            predicted_count = count_extended_fingers(hand)
            predicted_command = command_from_extended_count(predicted_count)
            cases.append(
                {
                    "extended_count": extended_count,
                    "rotation_deg": rotation_deg,
                    "expected_command": expected_command.value,
                    "predicted_count": predicted_count,
                    "predicted_command": predicted_command.value,
                    "correct": predicted_count == extended_count and predicted_command is expected_command,
                }
            )
    return cases


def transition_count(commands: list[Command]) -> int:
    return sum(a is not b for a, b in zip(commands, commands[1:]))


def stabilization_case() -> dict:
    stabilizer = CommandStabilizer(stable_frames_required=4)
    sequence: list[tuple[Command, bool]] = [
        (Command.FORWARD, True),
        (Command.FORWARD, True),
        (Command.FORWARD, True),
        (Command.FORWARD, True),
        (Command.LEFT, True),       # one-frame classification glitch
        (Command.FORWARD, True),
        (Command.REVERSE, True),    # another one-frame glitch
        (Command.FORWARD, True),
        (Command.RIGHT, True),
        (Command.RIGHT, True),
        (Command.RIGHT, True),
        (Command.RIGHT, True),      # legitimate stable change
        (Command.FORWARD, False),   # hand loss must stop immediately
    ]
    raw = [command for command, _ in sequence]
    outputs: list[Command] = []
    records = []
    for frame_index, (observed, hand_present) in enumerate(sequence, start=1):
        decision = stabilizer.update(observed, hand_present=hand_present)
        outputs.append(decision.output)
        records.append(
            {
                "frame": frame_index,
                "hand_present": hand_present,
                "observed": observed.value,
                "output": decision.output.value,
                "reason": decision.reason,
                "candidate_frames": decision.candidate_frames,
            }
        )

    return {
        "stable_frames_required": 4,
        "raw_transition_count": transition_count(raw),
        "output_transition_count": transition_count(outputs),
        "single_frame_glitches_suppressed": outputs[4] is Command.FORWARD and outputs[6] is Command.FORWARD,
        "stable_right_command_accepted": outputs[11] is Command.RIGHT,
        "hand_loss_stops_immediately": outputs[12] is Command.STOP,
        "frames": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/synthetic-gesture-evidence.json"))
    args = parser.parse_args()

    geometry = geometry_cases()
    correct = sum(case["correct"] for case in geometry)
    stabilization = stabilization_case()
    report = {
        "schema_version": 1,
        "evidence_type": "synthetic_gesture_geometry_and_stabilization_validation",
        "hardware_evidence": False,
        "real_camera_dataset": False,
        "claim_boundary": (
            "Synthetic landmarks verify ideal geometry rotation invariance and temporal command logic only. "
            "They do not measure MediaPipe recognition accuracy, camera latency, serial latency, or robot motion."
        ),
        "geometry": {
            "cases": len(geometry),
            "correct": correct,
            "accuracy": correct / len(geometry),
            "rotation_step_deg": 15,
            "results": geometry,
        },
        "stabilization": stabilization,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "geometry_cases": len(geometry),
                "geometry_accuracy": report["geometry"]["accuracy"],
                "stabilization": {k: v for k, v in stabilization.items() if k != "frames"},
            },
            indent=2,
            sort_keys=True,
        )
    )
    if correct != len(geometry):
        raise SystemExit(1)
    if not stabilization["single_frame_glitches_suppressed"]:
        raise SystemExit(1)
    if not stabilization["hand_loss_stops_immediately"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
