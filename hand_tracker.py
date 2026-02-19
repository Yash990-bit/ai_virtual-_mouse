import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

from collections import deque

class HandTracker:
    def __init__(self, model_path='hand_landmarker.task', max_hands=1, detection_con=0.5, track_con=0.5):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_con,
            min_hand_presence_confidence=track_con,
            running_mode=vision.RunningMode.VIDEO
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None
        self.tip_ids = [4, 8, 12, 16, 20]
        self.max_hands = max_hands

        # Pre-allocate histories for max_hands
        self.lm_histories = [[deque(maxlen=5) for _ in range(21)] for _ in range(max_hands)]
        self.finger_histories = [deque(maxlen=5) for _ in range(max_hands)]
        self.jitter_threshold = 2 # Pixels

    def find_hands(self, img, draw=True, timestamp_ms=0):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        self.results = self.detector.detect_for_video(mp_image, int(timestamp_ms))

        if draw and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                h, w, _ = img.shape
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8), # Index
                    (5, 9), (9, 10), (10, 11), (11, 12), # Middle
                    (9, 13), (13, 14), (14, 15), (15, 16), # Ring
                    (13, 17), (17, 18), (18, 19), (19, 20), # Pinky
                    (0, 5), (0, 17), (5, 17) # Palm
                ]
                for start, end in connections:
                    p1 = (int(hand_landmarks[start].x * w), int(hand_landmarks[start].y * h))
                    p2 = (int(hand_landmarks[end].x * w), int(hand_landmarks[end].y * h))
                    cv2.line(img, p1, p2, (0, 255, 0), 2)
                
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                h, w, c = img.shape
                
                # Get history for this specific hand
                current_lm_history = self.lm_histories[hand_no]
                
                for id, lm in enumerate(my_hand):
                    # Raw pixel coordinates
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    
                    # Temporal Smoothing
                    current_lm_history[id].append((cx, cy))
                    
                    # Weighted Moving Average
                    history_len = len(current_lm_history[id])
                    if history_len > 1:
                        weights = np.linspace(0.5, 1.0, history_len)
                        avg_x = sum(p[0] * weights[i] for i, p in enumerate(current_lm_history[id])) / sum(weights)
                        avg_y = sum(p[1] * weights[i] for i, p in enumerate(current_lm_history[id])) / sum(weights)
                        
                        if abs(avg_x - current_lm_history[id][-2][0]) > self.jitter_threshold or \
                           abs(avg_y - current_lm_history[id][-2][1]) > self.jitter_threshold:
                            cx, cy = int(avg_x), int(avg_y)
                        else:
                            cx, cy = current_lm_history[id][-2]
                    
                    lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lm_list

    def fingers_up(self, lm_list, hand_no=0):
        if not lm_list:
            return [0, 0, 0, 0, 0]
            
        raw_fingers = []
        # Thumb: depends on which hand it is (left/right) - simple check for now
        if lm_list[4][1] > lm_list[3][1] + 5:
            raw_fingers.append(1)
        else:
            raw_fingers.append(0)

        # 4 Fingers
        for id in range(1, 5):
            if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                raw_fingers.append(1)
            else:
                raw_fingers.append(0)
        
        # Stability check for this specific hand
        if hand_no < len(self.finger_histories):
            history = self.finger_histories[hand_no]
            history.append(tuple(raw_fingers))
            
            gesture_counts = {}
            for g in history:
                gesture_counts[g] = gesture_counts.get(g, 0) + 1
            stable_fingers = max(gesture_counts, key=gesture_counts.get)
            return list(stable_fingers)
            
        return raw_fingers
