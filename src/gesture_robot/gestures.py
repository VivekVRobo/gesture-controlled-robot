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


def count_extended_fingers(hand_landmarks) -> int:
    """Count index/middle/ring/pinky fingers using MediaPipe landmark geometry.

    A finger is considered extended when its tip is above its PIP joint in the
    image coordinate system. Thumb is intentionally excluded to reduce
    handedness/orientation sensitivity.
    """
    tip_ids = (8, 12, 16, 20)
    pip_ids = (6, 10, 14, 18)
    return sum(
        1 for tip, pip in zip(tip_ids, pip_ids)
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y
    )
