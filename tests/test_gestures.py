import pytest

from gesture_robot.gestures import Command, command_from_extended_count


def test_gesture_map():
    assert command_from_extended_count(0) == Command.STOP
    assert command_from_extended_count(1) == Command.LEFT
    assert command_from_extended_count(2) == Command.RIGHT
    assert command_from_extended_count(3) == Command.REVERSE
    assert command_from_extended_count(4) == Command.FORWARD


def test_invalid_count():
    with pytest.raises(ValueError):
        command_from_extended_count(5)
