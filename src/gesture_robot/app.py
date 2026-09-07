import argparse

from .gestures import LABELS, Command, command_from_extended_count, count_extended_fingers
from .protocol import CommandSender
from .stabilizer import CommandStabilizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control a robot from webcam hand gestures")
    parser.add_argument("--port", help="Serial port, e.g. COM5 or /dev/ttyACM0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true", help="Do not open a serial port")
    parser.add_argument(
        "--stable-frames",
        type=int,
        default=4,
        help="Consecutive frames required before a non-STOP motion command becomes active",
    )
    parser.add_argument("--detection-confidence", type=float, default=0.6)
    parser.add_argument("--tracking-confidence", type=float, default=0.6)
    return parser


def run() -> None:
    args = build_parser().parse_args()

    if args.stable_frames < 1:
        raise SystemExit("--stable-frames must be >= 1")
    if not 0.0 <= args.detection_confidence <= 1.0:
        raise SystemExit("--detection-confidence must be within [0, 1]")
    if not 0.0 <= args.tracking_confidence <= 1.0:
        raise SystemExit("--tracking-confidence must be within [0, 1]")

    import cv2
    import mediapipe as mp

    serial_handle = None
    if not args.dry_run:
        if not args.port:
            raise SystemExit("--port is required unless --dry-run is used")
        import serial
        serial_handle = serial.Serial(args.port, args.baud, timeout=0.1)

    sender = CommandSender(serial_handle)
    stabilizer = CommandStabilizer(stable_frames_required=args.stable_frames)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    hands_api = mp.solutions.hands
    drawing = mp.solutions.drawing_utils

    try:
        with hands_api.Hands(
            max_num_hands=1,
            min_detection_confidence=args.detection_confidence,
            min_tracking_confidence=args.tracking_confidence,
        ) as hands:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv2.flip(frame, 1)
                result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                hand_present = bool(result.multi_hand_landmarks)
                raw_command = Command.STOP
                count = 0
                if hand_present:
                    hand = result.multi_hand_landmarks[0]
                    count = count_extended_fingers(hand)
                    raw_command = command_from_extended_count(count)
                    drawing.draw_landmarks(frame, hand, hands_api.HAND_CONNECTIONS)

                decision = stabilizer.update(raw_command, hand_present=hand_present)
                sender.send(decision.output)

                cv2.putText(
                    frame,
                    f"Fingers: {count}  Raw: {LABELS[raw_command]}  Output: {LABELS[decision.output]}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.68,
                    (255, 255, 255),
                    2,
                )
                cv2.putText(
                    frame,
                    f"State: {decision.reason} ({decision.candidate_frames}/{args.stable_frames})",
                    (20, 72),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    1,
                )
                cv2.imshow("Gesture Controlled Robot", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        stabilizer.update(Command.STOP, hand_present=False)
        sender.send(Command.STOP, force=True)
        cap.release()
        cv2.destroyAllWindows()
        if serial_handle is not None:
            serial_handle.close()


if __name__ == "__main__":
    run()
