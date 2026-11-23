import pytest

from gesture_robot.gestures import Command
from gesture_robot.protocol import CommandSender, encode_command


def test_encoding():
    assert encode_command(Command.FORWARD) == b"F\n"
    assert encode_command(Command.STOP) == b"S\n"


def test_sender_rejects_invalid_rate_limit():
    with pytest.raises(ValueError):
        CommandSender(min_interval_s=-0.01)

    with pytest.raises(ValueError):
        CommandSender(min_interval_s=float("nan"))

    with pytest.raises(ValueError):
        CommandSender(min_interval_s=float("inf"))


def test_sender_allows_zero_rate_limit():
    sender = CommandSender(min_interval_s=0)
    assert sender.send(Command.FORWARD)
