import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

class FaceTracker:
    def __init__(self, model_path='face_landmarker.task', running_mode=vision.RunningMode.VIDEO):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True,
            num_faces=1,
            running_mode=running_mode
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
        self.results = None

    def find_face(self, img, timestamp_ms):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
        self.results = self.detector.detect_for_video(mp_image, int(timestamp_ms))
        return self.results

    def get_blink_status(self):
        """
        Returns (left_blink, right_blink) as booleans.
        Uses blendshapes for high accuracy.
        """
        left_blink = False
        right_blink = False
        
        if self.results and self.results.face_blendshapes:
            blendshapes = self.results.face_blendshapes[0]
            for shape in blendshapes:
                if shape.category_name == 'eyeBlinkLeft':
                    
                    if shape.score > 0.5:
                        left_blink = True
                if shape.category_name == 'eyeBlinkRight':
                    if shape.score > 0.5:
                        right_blink = True
                        
        return left_blink, right_blink

    def draw_face_info(self, img):
        if self.results and self.results.face_landmarks:
            for face_landmarks in self.results.face_landmarks:
                h, w, _ = img.shape
                
                for id in [362, 33]:
                    lm = face_landmarks[id]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(img, (cx, cy), 3, (255, 255, 0), cv2.FILLED)
        return img
