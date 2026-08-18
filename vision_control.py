import argparse
import time

import cv2
import mediapipe as mp
import serial

COMMANDS = {
    "forward": "F",
    "backward": "B",
    "left": "L",
    "right": "R",
    "stop": "S",
}


def finger_states(hand):
    lm = hand.landmark
    # Index/middle/ring/pinky: fingertip above PIP in image coordinates.
    fingers = [lm[tip].y < lm[pip].y for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]]
    # Thumb estimate based on horizontal separation; adequate for a simple demo,
    # but handedness-aware logic can improve this later.
    thumb = abs(lm[4].x - lm[2].x) > 0.08
    return [thumb, *fingers]


def classify(states):
    thumb, index, middle, ring, pinky = states
    if all(states):
        return "forward"
    if not any(states):
        return "stop"
    if index and not any([thumb, middle, ring, pinky]):
        return "left"
    if index and middle and not any([thumb, ring, pinky]):
        return "right"
    if thumb and not any([index, middle, ring, pinky]):
        return "backward"
    return "stop"


def main():
    parser = argparse.ArgumentParser(description="Control a differential-drive robot with hand gestures")
    parser.add_argument("--port", help="Serial port, e.g. COM5 or /dev/ttyUSB0")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.port:
        parser.error("--port is required unless --dry-run is used")

    link = None if args.dry_run else serial.Serial(args.port, args.baud, timeout=0.1)
    if link:
        time.sleep(2.0)

    cap = cv2.VideoCapture(args.camera)
    hands_module = mp.solutions.hands
    drawer = mp.solutions.drawing_utils
    last_command = None
    last_seen = time.monotonic()

    def send(command):
        nonlocal last_command
        if command == last_command:
            return
        last_command = command
        print(f"command={command}")
        if link:
            link.write((COMMANDS[command] + "\n").encode("ascii"))

    try:
        with hands_module.Hands(max_num_hands=1, min_detection_confidence=0.65, min_tracking_confidence=0.65) as hands:
            while cap.isOpened():
                ok, frame = cap.read()
                if not ok:
                    break
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb)

                command = "stop"
                if result.multi_hand_landmarks:
                    hand = result.multi_hand_landmarks[0]
                    last_seen = time.monotonic()
                    command = classify(finger_states(hand))
                    drawer.draw_landmarks(frame, hand, hands_module.HAND_CONNECTIONS)
                elif time.monotonic() - last_seen > 0.25:
                    command = "stop"

                send(command)
                cv2.putText(frame, command.upper(), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                cv2.imshow("Gesture Robot", frame)
                if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
    finally:
        send("stop")
        cap.release()
        cv2.destroyAllWindows()
        if link:
            link.close()


if __name__ == "__main__":
    main()
