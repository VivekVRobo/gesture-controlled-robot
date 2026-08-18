import argparse

from .gestures import LABELS, Command, command_from_extended_count, count_extended_fingers
from .protocol import CommandSender


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Control a robot from webcam hand gestures")
    p.add_argument("--port", help="Serial port, e.g. COM5 or /dev/ttyACM0")
    p.add_argument("--baud", type=int, default=115200)
    p.add_argument("--camera", type=int, default=0)
    p.add_argument("--dry-run", action="store_true", help="Do not open a serial port")
    return p


def run() -> None:
    args = build_parser().parse_args()

    import cv2
    import mediapipe as mp

    serial_handle = None
    if not args.dry_run:
        if not args.port:
            raise SystemExit("--port is required unless --dry-run is used")
        import serial
        serial_handle = serial.Serial(args.port, args.baud, timeout=0.1)

    sender = CommandSender(serial_handle)
    cap = cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        raise SystemExit(f"Could not open camera {args.camera}")

    hands_api = mp.solutions.hands
    drawing = mp.solutions.drawing_utils

    try:
        with hands_api.Hands(max_num_hands=1, min_detection_confidence=0.6,
                             min_tracking_confidence=0.6) as hands:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv2.flip(frame, 1)
                result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                command = Command.STOP
                count = 0
                if result.multi_hand_landmarks:
                    hand = result.multi_hand_landmarks[0]
                    count = count_extended_fingers(hand)
                    command = command_from_extended_count(count)
                    drawing.draw_landmarks(frame, hand, hands_api.HAND_CONNECTIONS)

                sender.send(command)
                cv2.putText(frame, f"Fingers: {count}  Command: {LABELS[command]}",
                            (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.imshow("Gesture Controlled Robot", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    finally:
        sender.send(Command.STOP, force=True)
        cap.release()
        cv2.destroyAllWindows()
        if serial_handle is not None:
            serial_handle.close()


if __name__ == "__main__":
    run()
