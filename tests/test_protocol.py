from gesture_robot.gestures import Command
from gesture_robot.protocol import CommandSender, encode_command


def test_encoding():
    assert encode_command(Command.FORWARD) == b"F\n"
    assert encode_command(Command.STOP) == b"S\n"


class FakeSerial:
    def __init__(self):
        self.writes = []

    def write(self, payload):
        self.writes.append(payload)


def test_command_sender_sends_changed_command_immediately(monkeypatch):
    clock = iter([10.0, 10.01])
    monkeypatch.setattr("gesture_robot.protocol.time.monotonic", lambda: next(clock))

    serial = FakeSerial()
    sender = CommandSender(serial_port=serial, min_interval_s=1.0)

    assert sender.send(Command.FORWARD) is True
    assert sender.send(Command.LEFT) is True
    assert serial.writes == [b"F\n", b"L\n"]


def test_command_sender_rate_limits_unchanged_command(monkeypatch):
    clock = iter([20.0, 20.5, 21.01])
    monkeypatch.setattr("gesture_robot.protocol.time.monotonic", lambda: next(clock))

    serial = FakeSerial()
    sender = CommandSender(serial_port=serial, min_interval_s=1.0)

    assert sender.send(Command.FORWARD) is True
    assert sender.send(Command.FORWARD) is False
    assert sender.send(Command.FORWARD) is True
    assert serial.writes == [b"F\n", b"F\n"]


def test_command_sender_force_bypasses_rate_limit(monkeypatch):
    clock = iter([30.0, 30.1])
    monkeypatch.setattr("gesture_robot.protocol.time.monotonic", lambda: next(clock))

    serial = FakeSerial()
    sender = CommandSender(serial_port=serial, min_interval_s=1.0)

    assert sender.send(Command.STOP) is True
    assert sender.send(Command.STOP, force=True) is True
    assert serial.writes == [b"S\n", b"S\n"]
