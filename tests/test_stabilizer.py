import pytest

from gesture_robot.gestures import Command
from gesture_robot.stabilizer import CommandStabilizer


def test_motion_requires_stable_frames_but_stop_is_immediate():
    stabilizer = CommandStabilizer(stable_frames_required=3)

    assert stabilizer.update(Command.FORWARD).output is Command.STOP
    assert stabilizer.update(Command.FORWARD).output is Command.STOP
    activated = stabilizer.update(Command.FORWARD)
    assert activated.output is Command.FORWARD
    assert activated.changed

    glitch = stabilizer.update(Command.LEFT)
    assert glitch.output is Command.FORWARD
    assert not glitch.changed

    stop = stabilizer.update(Command.STOP)
    assert stop.output is Command.STOP
    assert stop.changed
    assert stop.reason == "immediate-stop"


def test_hand_loss_forces_stop_without_waiting_for_debounce():
    stabilizer = CommandStabilizer(stable_frames_required=2)
    stabilizer.update(Command.REVERSE)
    assert stabilizer.update(Command.REVERSE).output is Command.REVERSE

    lost = stabilizer.update(Command.REVERSE, hand_present=False)
    assert lost.output is Command.STOP
    assert lost.reason == "hand-lost-stop"


def test_candidate_change_restarts_counter():
    stabilizer = CommandStabilizer(stable_frames_required=3)
    assert stabilizer.update(Command.LEFT).candidate_frames == 1
    assert stabilizer.update(Command.LEFT).candidate_frames == 2
    changed_candidate = stabilizer.update(Command.RIGHT)
    assert changed_candidate.output is Command.STOP
    assert changed_candidate.candidate_frames == 1


def test_invalid_stable_frame_configuration():
    with pytest.raises(ValueError):
        CommandStabilizer(stable_frames_required=0)
