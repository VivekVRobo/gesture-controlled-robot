import time
from dataclasses import dataclass
from typing import Optional

from .gestures import Command


def encode_command(command: Command) -> bytes:
    return f"{command.value}\n".encode("ascii")


@dataclass
class CommandSender:
    serial_port: Optional[object] = None
    min_interval_s: float = 0.08
    _last_command: Optional[Command] = None
    _last_sent_at: float = 0.0

    def send(self, command: Command, *, force: bool = False) -> bool:
        now = time.monotonic()
        changed = command != self._last_command
        due = (now - self._last_sent_at) >= self.min_interval_s
        if not force and not changed and not due:
            return False

        payload = encode_command(command)
        if self.serial_port is not None:
            self.serial_port.write(payload)
        else:
            print(f"DRY-RUN {payload.decode().strip()}")

        self._last_command = command
        self._last_sent_at = now
        return True
