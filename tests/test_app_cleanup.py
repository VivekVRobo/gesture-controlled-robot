from types import SimpleNamespace
import sys

import pytest

from gesture_robot import app


class FakeSerial:
    def __init__(self, *, fail_write=False):
        self.fail_write = fail_write
        self.writes = []
        self.closed = False

    def write(self, payload):
        if self.fail_write:
            raise OSError("serial disconnected")
        self.writes.append(payload)

    def close(self):
        self.closed = True


class FakeCapture:
    def __init__(self, opened):
        self.opened = opened
        self.released = False

    def isOpened(self):
        return self.opened

    def release(self):
        self.released = True


class FakeHandsContext:
    def __enter__(self):
        raise RuntimeError("pipeline initialization failed")

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeHandsAPI:
    HAND_CONNECTIONS = ()

    def Hands(self, **kwargs):
        return FakeHandsContext()


def configure_run(monkeypatch, *, camera_opened, fail_serial_write=False):
    serial_handle = FakeSerial(fail_write=fail_serial_write)
    capture = FakeCapture(opened=camera_opened)
    state = {"windows_destroyed": False}
    fake_cv2 = SimpleNamespace(
        VideoCapture=lambda camera: capture,
        destroyAllWindows=lambda: state.update(windows_destroyed=True),
    )
    fake_mp = SimpleNamespace(
        solutions=SimpleNamespace(
            hands=FakeHandsAPI(),
            drawing_utils=SimpleNamespace(draw_landmarks=lambda *args, **kwargs: None),
        )
    )
    fake_serial_module = SimpleNamespace(
        Serial=lambda *args, **kwargs: serial_handle,
    )
    args = SimpleNamespace(
        dry_run=False,
        port="COM5",
        baud=115200,
        camera=0,
        stable_frames=4,
        detection_confidence=0.6,
        tracking_confidence=0.6,
    )

    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    monkeypatch.setitem(sys.modules, "mediapipe", fake_mp)
    monkeypatch.setitem(sys.modules, "serial", fake_serial_module)
    monkeypatch.setattr(
        app,
        "build_parser",
        lambda: SimpleNamespace(parse_args=lambda: args),
    )
    return serial_handle, capture, state


def test_camera_open_failure_stops_and_closes_serial(monkeypatch):
    serial_handle, capture, state = configure_run(monkeypatch, camera_opened=False)

    with pytest.raises(SystemExit, match="Could not open camera 0"):
        app.run()

    assert serial_handle.writes == [b"S\n"]
    assert serial_handle.closed
    assert capture.released
    assert state["windows_destroyed"]


def test_failed_stop_write_does_not_skip_resource_cleanup(monkeypatch):
    serial_handle, capture, state = configure_run(
        monkeypatch,
        camera_opened=True,
        fail_serial_write=True,
    )

    with pytest.raises(OSError, match="serial disconnected"):
        app.run()

    assert capture.released
    assert state["windows_destroyed"]
    assert serial_handle.closed
