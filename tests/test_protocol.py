from gesture_robot.gestures import Command
from gesture_robot.protocol import encode_command


def test_encoding():
    assert encode_command(Command.FORWARD) == b"F\n"
    assert encode_command(Command.STOP) == b"S\n"
