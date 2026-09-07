from __future__ import annotations

from dataclasses import dataclass

from .gestures import Command


@dataclass(frozen=True)
class StabilizerDecision:
    observed: Command
    output: Command
    changed: bool
    reason: str
    candidate_frames: int


@dataclass
class CommandStabilizer:
    """Debounce motion gestures while preserving immediate STOP behavior.

    Motion commands must be observed for ``stable_frames_required`` consecutive
    frames before becoming active. STOP is always immediate, including when the
    hand disappears, so temporal smoothing cannot delay a fail-safe stop.
    """

    stable_frames_required: int = 4
    _output: Command = Command.STOP
    _candidate: Command | None = None
    _candidate_frames: int = 0

    def __post_init__(self) -> None:
        if self.stable_frames_required < 1:
            raise ValueError("stable_frames_required must be >= 1")

    @property
    def output(self) -> Command:
        return self._output

    def reset(self) -> None:
        self._output = Command.STOP
        self._candidate = None
        self._candidate_frames = 0

    def update(self, observed: Command, *, hand_present: bool = True) -> StabilizerDecision:
        if not hand_present or observed is Command.STOP:
            changed = self._output is not Command.STOP
            self._output = Command.STOP
            self._candidate = None
            self._candidate_frames = 0
            return StabilizerDecision(
                observed=observed,
                output=self._output,
                changed=changed,
                reason="immediate-stop" if hand_present else "hand-lost-stop",
                candidate_frames=0,
            )

        if observed is self._output:
            self._candidate = None
            self._candidate_frames = 0
            return StabilizerDecision(observed, self._output, False, "already-stable", 0)

        if observed is self._candidate:
            self._candidate_frames += 1
        else:
            self._candidate = observed
            self._candidate_frames = 1

        if self._candidate_frames >= self.stable_frames_required:
            self._output = observed
            self._candidate = None
            frames = self._candidate_frames
            self._candidate_frames = 0
            return StabilizerDecision(observed, self._output, True, "motion-stabilized", frames)

        return StabilizerDecision(
            observed,
            self._output,
            False,
            "stabilizing-motion",
            self._candidate_frames,
        )
