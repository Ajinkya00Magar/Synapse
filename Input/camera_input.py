import os
import sys
import collections

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import (
    HandLandmarker,
    HandLandmarkerOptions,
    HandLandmarkerResult,
    HandLandmarksConnections,
    RunningMode,
    drawing_utils,
)
from mediapipe.tasks.python.vision.drawing_utils import DrawingSpec
from mediapipe.tasks import python as mp_python

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hand_landmarker.task")

MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

SMOOTHING_WINDOW = 5

WRIST = 0
THUMB_CMC = 1
THUMB_MCP = 2
THUMB_IP = 3
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12
RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20


def get_finger_states(landmarks, handedness: str) -> dict[str, bool]:
    index = landmarks[INDEX_TIP].y < landmarks[INDEX_PIP].y
    middle = landmarks[MIDDLE_TIP].y < landmarks[MIDDLE_PIP].y
    ring = landmarks[RING_TIP].y < landmarks[RING_PIP].y
    pinky = landmarks[PINKY_TIP].y < landmarks[PINKY_PIP].y

    if handedness == "Right":
        thumb = landmarks[THUMB_TIP].x > landmarks[THUMB_MCP].x
    else:
        thumb = landmarks[THUMB_TIP].x < landmarks[THUMB_MCP].x

    return {
        "thumb": thumb,
        "index": index,
        "middle": middle,
        "ring": ring,
        "pinky": pinky,
    }


def classify_gesture(finger_states: dict[str, bool], landmarks) -> str:
    thumb = finger_states["thumb"]
    index = finger_states["index"]
    middle = finger_states["middle"]
    ring = finger_states["ring"]
    pinky = finger_states["pinky"]

    if thumb and index and middle and ring and pinky:
        return "Open Palm"

    if index and middle and not ring and not pinky and not thumb:
        return "Peace Sign"

    if thumb and not index and not middle and not ring and not pinky:
        if landmarks[THUMB_TIP].y < landmarks[WRIST].y:
            return "Thumbs Up"
        else:
            return "Thumbs Down"

    return "Unknown"



LANDMARK_STYLE = DrawingSpec(color=(0, 255, 128), thickness=2, circle_radius=3)
CONNECTION_STYLE = DrawingSpec(color=(255, 200, 0), thickness=2, circle_radius=1)

GESTURE_COLORS = {
    "Thumbs Up": (0, 220, 0),      # green
    "Thumbs Down": (0, 0, 220),    # red
    "Open Palm": (255, 180, 0),    # cyan-ish
    "Peace Sign": (255, 100, 255), # magenta
    "Unknown": (180, 180, 180),    # gray
}

# Gesture emoji map
GESTURE_EMOJI = {
    "Thumbs Up": "👍",
    "Thumbs Down": "👎",
    "Open Palm": "✋",
    "Peace Sign": "✌️",
    "Unknown": "🤷",
}


def draw_gesture_label(frame, gesture: str):
    color = GESTURE_COLORS.get(gesture, (180, 180, 180))
    emoji = GESTURE_EMOJI.get(gesture, "")

    # Background bar
    cv2.rectangle(frame, (0, 0), (400, 60), (30, 30, 30), -1)

    # Gesture text
    label = f"{emoji}  {gesture}"
    cv2.putText(
        frame, label, (15, 42),
        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3, cv2.LINE_AA,
    )


def draw_hand_landmarks(frame, hand_landmarks):
    drawing_utils.draw_landmarks(
        image=frame,
        landmark_list=hand_landmarks,
        connections=HandLandmarksConnections.HAND_CONNECTIONS,
        landmark_drawing_spec=LANDMARK_STYLE,
        connection_drawing_spec=CONNECTION_STYLE,
    )


def main():
    # Verify model file exists
    if not os.path.isfile(MODEL_PATH):
        print(f"ERROR: Model file not found at: {MODEL_PATH}")
        print("Download it with:")
        print("  Invoke-WebRequest -Uri 'https://storage.googleapis.com/mediapipe-models/"
              "hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task' "
              f"-OutFile '{MODEL_PATH}'")
        sys.exit(1)

    # 1. Create the HandLandmarker
    options = HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
    )
    landmarker = HandLandmarker.create_from_options(options)

    # 2. Open the webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Could not open webcam.")
        sys.exit(1)

    # Set resolution (optional — adjust to your camera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 3. Gesture smoothing buffer
    gesture_buffer = collections.deque(maxlen=SMOOTHING_WINDOW)
    last_printed_gesture = None
    frame_timestamp_ms = 0

    print("\n" + "=" * 50)
    print("  📷 Hand Gesture Detection")
    print("=" * 50)
    print("\nCamera is open. Show your hand to detect gestures.")
    print("Press Q or ESC to quit.\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read from webcam.")
                break

            # Flip horizontally for a mirror-like experience
            frame = cv2.flip(frame, 1)

            # Convert BGR → RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Detect hand landmarks
            frame_timestamp_ms += 33  # ~30 FPS
            result: HandLandmarkerResult = landmarker.detect_for_video(
                mp_image, frame_timestamp_ms
            )

            current_gesture = "No Hand"

            if result.hand_landmarks and result.handedness:
                for i, hand_landmarks in enumerate(result.hand_landmarks):
                    # Get handedness label
                    handedness_label = result.handedness[i][0].category_name

                    # Draw landmarks on frame
                    draw_hand_landmarks(frame, hand_landmarks)

                    # Determine finger states and classify gesture
                    finger_states = get_finger_states(hand_landmarks, handedness_label)
                    current_gesture = classify_gesture(finger_states, hand_landmarks)

            # Smooth gesture output
            gesture_buffer.append(current_gesture)
            # Pick the most common gesture in the buffer
            smoothed_gesture = collections.Counter(gesture_buffer).most_common(1)[0][0]

            # Draw label on frame
            if smoothed_gesture != "No Hand":
                draw_gesture_label(frame, smoothed_gesture)
            else:
                # Show "No hand detected" in gray
                cv2.rectangle(frame, (0, 0), (400, 60), (30, 30, 30), -1)
                cv2.putText(
                    frame, "No hand detected", (15, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (120, 120, 120), 2, cv2.LINE_AA,
                )

            # Print to console when gesture changes
            if smoothed_gesture != last_printed_gesture:
                if smoothed_gesture != "No Hand" and smoothed_gesture != "Unknown":
                    emoji = GESTURE_EMOJI.get(smoothed_gesture, "")
                    print(f"  {emoji}  Gesture: {smoothed_gesture}")
                last_printed_gesture = smoothed_gesture

            # Show the frame
            cv2.imshow("Synapse — Gesture Detection", frame)

            # Check for quit keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:  # Q or ESC
                break

    except KeyboardInterrupt:
        print("\n⏹️  Interrupted.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        landmarker.close()
        print("Camera closed. Done.")


if __name__ == "__main__":
    main()
