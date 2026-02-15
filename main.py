import cv2
import numpy as np
from hand_tracker import HandTracker
from mouse_controller import MouseController
from system_controller import SystemController
from ui_panel import start_ui
import time
import threading

# Global settings for real-time updates from UI
settings = {
    "smoothing": 7,
    "detection_con": 0.8
}

def ui_thread_func():
    def update_callback(new_settings):
        global settings
        settings.update(new_settings)
    start_ui(update_callback)

def main():
    # Constants
    V_WIDTH, V_HEIGHT = 640, 480
    FRAME_MARGIN = 100
    
    # Start UI in a separate thread
    ui_thread = threading.Thread(target=ui_thread_func, daemon=True)
    ui_thread.start()
    
    # Initialize components
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    cap.set(3, V_WIDTH)
    cap.set(4, V_HEIGHT)
    
    tracker = HandTracker(max_hands=1, detection_con=settings["detection_con"])
    mouse = MouseController(smoothing=settings["smoothing"])
    sys_ctrl = SystemController()
    
    p_time = 0
    
    print("AI Virtual Mouse Started. Press 'q' on the video window to quit.")
    
    while True:
        # Update dynamically from settings
        tracker.hands.min_detection_confidence = settings["detection_con"]
        mouse.smoothing = settings["smoothing"]

        success, img = cap.read()
        if not success:
            break
            
        img = cv2.flip(img, 1) # Flip to act like a mirror
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            # Tip of Index Finger (8) and Middle Finger (12)
            x1, y1 = lm_list[8][1], lm_list[8][2]
            x2, y2 = lm_list[12][1], lm_list[12][2]
            
            # Check which fingers are up
            # Note: HandTracker.fingers_up depends on self.lm_list being populated by find_position
            fingers = tracker.fingers_up()
            
            # Index Finger Up: Moving Mode
            if fingers[1] == 1 and fingers[2] == 0:
                mouse.move_cursor(x1, y1, V_WIDTH, V_HEIGHT, margin=FRAME_MARGIN)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)

            # Index & Middle Fingers Up: Clicking Mode
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                # Calculate distance between index and middle tips
                dist = np.hypot(x2 - x1, y2 - y1)
                
                # If distance is small, perform click
                if dist < 40:
                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                    mouse.click()
                    time.sleep(0.1)

            # Index, Middle and Ring up: Right Click
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                mouse.right_click()
                time.sleep(0.3)

            # Index and Thumb up: Volume Control
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                vol_level = int(np.interp(y1, (50, V_HEIGHT - 50), (100, 0)))
                sys_ctrl.volume_control(vol_level)
                cv2.putText(img, f"Volume: {vol_level}", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

            # Pinky and Thumb up: Screenshot
            elif fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                sys_ctrl.take_screenshot()
                cv2.putText(img, "Screenshot Captured!", (200, 240), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                time.sleep(0.5)

            # All fingers up except thumb: Scroll Mode
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and fingers[0] == 0:
                if y1 < V_HEIGHT // 2:
                    mouse.scroll('up')
                else:
                    mouse.scroll('down')

        # FPS calculation
        c_time = time.time()
        fps = 1 / (c_time - p_time)
        p_time = c_time
        
        cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.imshow("AI Virtual Mouse", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
