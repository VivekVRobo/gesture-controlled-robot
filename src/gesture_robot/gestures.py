from __future__ import annotations

import math
from enum import Enum


class Command(str, Enum):
    STOP = "S"
    FORWARD = "F"
    REVERSE = "B"
    LEFT = "L"
    RIGHT = "R"


LABELS = {
    Command.STOP: "STOP",
    Command.FORWARD: "FORWARD",
    Command.REVERSE: "REVERSE",
    Command.LEFT: "LEFT",
    Command.RIGHT: "RIGHT",
}


FINGER_JOINTS = (
    (5, 6, 8),   # index: MCP, PIP, tip
    (9, 10, 12), # middle
    (13, 14, 16),
    (17, 18, 20),
)


def command_from_extended_count(count: int) -> Command:
    """Map the number of extended non-thumb fingers to a robot command."""
    mapping = {
        0: Command.STOP,
        1: Command.LEFT,
        2: Command.RIGHT,
        3: Command.REVERSE,
        4: Command.FORWARD,
    }
    if count not in mapping:
        raise ValueError("extended finger count must be between 0 and 4")
    return mapping[count]


def _xyz(landmark) -> tuple[float, float, float]:
    return (
        float(landmark.x),
        float(landmark.y),
        float(getattr(landmark, "z", 0.0)),
    )


def _sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def _norm(vector: tuple[float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return _norm(_sub(a, b))


def _angle_deg(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    na, nb = _norm(a), _norm(b)
    if na <= 1e-12 or nb <= 1e-12:
        return 0.0
    cosine = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b)) / (na * nb)))
    return math.degrees(math.acos(cosine))


def finger_is_extended(
    hand_landmarks,
    mcp_id: int,
    pip_id: int,
    tip_id: int,
    *,
    min_pip_angle_deg: float = 150.0,
    min_tip_distance_ratio: float = 1.05,
) -> bool:
    """Classify one non-thumb finger from landmark geometry.

    The old implementation relied on ``tip.y < pip.y``, which only works when
    fingers point upward in image coordinates. This implementation instead uses
    the PIP joint angle plus a wrist-distance guard, making the decision
    invariant to simple in-plane hand rotation in the ideal landmark model.
    """
    landmarks = hand_landmarks.landmark
    wrist = _xyz(landmarks[0])
    mcp = _xyz(landmarks[mcp_id])
    pip = _xyz(landmarks[pip_id])
    tip = _xyz(landmarks[tip_id])

    pip_angle = _angle_deg(_sub(mcp, pip), _sub(tip, pip))
    pip_distance = _distance(wrist, pip)
    tip_distance = _distance(wrist, tip)
    distance_ok = tip_distance >= pip_distance * min_tip_distance_ratio
    return pip_angle >= min_pip_angle_deg and distance_ok


def finger_extension_states(hand_landmarks) -> tuple[bool, bool, bool, bool]:
    return tuple(
        finger_is_extended(hand_landmarks, mcp, pip, tip)
        for mcp, pip, tip in FINGER_JOINTS
    )


def count_extended_fingers(hand_landmarks) -> int:
    """Count index/middle/ring/pinky using orientation-aware joint geometry.

    Thumb remains intentionally excluded so the command mapping does not depend
    on handedness-specific thumb geometry.
    """
    return sum(finger_extension_states(hand_landmarks))
