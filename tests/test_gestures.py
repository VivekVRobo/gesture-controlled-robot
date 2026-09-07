import math
from dataclasses import dataclass

import pytest

from gesture_robot.gestures import Command, command_from_extended_count, count_extended_fingers


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


def make_hand(extended_count: int, rotation_deg: float) -> Hand:
    points = [Point() for _ in range(21)]
    joints = ((5, 6, 8), (9, 10, 12), (13, 14, 16), (17, 18, 20))
    for index, ((mcp_id, pip_id, tip_id), x) in enumerate(zip(joints, (-0.30, -0.10, 0.10, 0.30))):
        points[mcp_id] = rotate(Point(x, -0.30), rotation_deg)
        points[pip_id] = rotate(Point(x, -0.60), rotation_deg)
        tip = Point(x, -1.00) if index < extended_count else Point(x, -0.34)
        points[tip_id] = rotate(tip, rotation_deg)
    return Hand(points)


def test_gesture_map():
    assert command_from_extended_count(0) == Command.STOP
    assert command_from_extended_count(1) == Command.LEFT
    assert command_from_extended_count(2) == Command.RIGHT
    assert command_from_extended_count(3) == Command.REVERSE
    assert command_from_extended_count(4) == Command.FORWARD


@pytest.mark.parametrize("rotation_deg", list(range(0, 360, 30)))
@pytest.mark.parametrize("extended_count", range(5))
def test_extended_finger_count_is_invariant_to_ideal_in_plane_rotation(extended_count, rotation_deg):
    hand = make_hand(extended_count, rotation_deg)
    assert count_extended_fingers(hand) == extended_count


def test_invalid_count():
    with pytest.raises(ValueError):
        command_from_extended_count(5)
