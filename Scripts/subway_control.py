import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

cap = cv2.VideoCapture(0)

# Set resolution for better accuracy
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Variables
gesture = ""
last_gesture_time = 0
cooldown = 0.5  # seconds

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    h, w, _ = frame.shape

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            lm = hand_landmarks.landmark

            # Count extended fingers
            fingers_extended = 0
            finger_ids = [
                (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
                (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
                (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
                (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
            ]

            for tip_id, pip_id in finger_ids:
                if lm[tip_id].y < lm[pip_id].y:
                    fingers_extended += 1

            # Optional: include thumb as 5th finger
            thumb_tip = lm[mp_hands.HandLandmark.THUMB_TIP]
            thumb_ip = lm[mp_hands.HandLandmark.THUMB_IP]
            if thumb_tip.x < thumb_ip.x:  # For right hand
                fingers_extended += 1

            # Get current time for cooldown
            now = time.time()

            # Action based on finger count
            if now - last_gesture_time > cooldown:
                if fingers_extended == 1:
                    pyautogui.press('w')
                    gesture = "Go Straight"
                    last_gesture_time = now

                elif fingers_extended == 2:
                    pyautogui.press('right')
                    gesture = "Move Right"
                    last_gesture_time = now

                elif fingers_extended == 3:
                    pyautogui.press('left')
                    gesture = "Move Left"
                    last_gesture_time = now

                elif fingers_extended == 4:
                    pyautogui.press('down')
                    gesture = "Roll"
                    last_gesture_time = now

                elif fingers_extended >= 5:
                    pyautogui.press('up')
                    gesture = "Jump"
                    last_gesture_time = now

    else:
        gesture = "No Hand Detected"

    # Display gesture on screen
    cv2.putText(frame, f"Gesture: {gesture}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow("Game Control", frame)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()