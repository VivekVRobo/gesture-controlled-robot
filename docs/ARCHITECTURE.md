# Architecture

The project is split at the serial boundary so both halves can be tested independently.

## Host

- `app.py`: camera loop, MediaPipe integration, display, shutdown behavior
- `gestures.py`: deterministic finger-count → command policy
- `protocol.py`: ASCII command framing and rate-limited sending

## Robot

The Arduino receives single-character commands and directly drives a differential H-bridge. A watchdog stops the motors if the host disappears or communication stalls.

## Why the protocol is intentionally small

A five-command ASCII protocol is easy to inspect in a serial terminal, easy to implement on small MCUs, and easy to recover after line noise. If telemetry or closed-loop control is added later, move to a framed protocol with checksums/versioning rather than extending this ad hoc indefinitely.
