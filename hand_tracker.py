import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

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
        self.lm_list = []
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, img, draw=True, timestamp_ms=0):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        self.results = self.detector.detect_for_video(mp_image, int(timestamp_ms))

        if draw and self.results.hand_landmarks:
            for hand_landmarks in self.results.hand_landmarks:
                h, w, _ = img.shape
                
                # Draw skeleton
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
                
                # Draw points
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        self.lm_list = []
        if self.results and self.results.hand_landmarks:
            if len(self.results.hand_landmarks) > hand_no:
                hand_landmarks = self.results.hand_landmarks[hand_no]
                h, w, _ = img.shape
                for id, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    self.lm_list.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return self.lm_list

    def fingers_up(self, lm_list=None):
        fingers = []
        target_lm_list = lm_list if lm_list is not None else self.lm_list
        
        if not target_lm_list:
            return [0, 0, 0, 0, 0]
            
        # Thumb: Threshold-based check for open thumb
        if target_lm_list[4][1] > target_lm_list[4-1][1] + 5:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers: Check tip relative to middle joint
        for id in range(1, 5):
            if target_lm_list[self.tip_ids[id]][2] < target_lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers
