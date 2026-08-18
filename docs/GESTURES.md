# Gesture Design

The reference classifier counts only index, middle, ring, and pinky extension. A finger is considered extended when its MediaPipe tip landmark is above its PIP landmark.

| Count | Motion |
|---:|---|
| 0 | Stop |
| 1 | Left |
| 2 | Right |
| 3 | Reverse |
| 4 | Forward |

## Limitations

This is a simple geometric classifier, not a trained gesture model. It can be affected by camera angle, occlusion, hand rotation, and lighting. For a stronger system, add temporal smoothing, confidence thresholds, a neutral/dead-man gesture, and dataset-based evaluation.
