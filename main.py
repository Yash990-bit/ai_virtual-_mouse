import cv2
import numpy as np
import time
from hand_tracker import HandTracker
from mouse_controller import MouseController
from system_controller import SystemController
from performance_monitor import PerformanceMonitor

def main():
    # --- Config ---
    V_WIDTH, V_HEIGHT = 640, 480
    FRAME_MARGIN = 100
    
    # --- Init ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ CAMERA ERROR: Could not access webcam.")
        return

    cap.set(3, V_WIDTH)
    cap.set(4, V_HEIGHT)
    
    tracker = HandTracker(max_hands=1, detection_con=0.7)
    mouse = MouseController(smoothing=7)
    sys_ctrl = SystemController()
    perf_mon = PerformanceMonitor()
    
    p_time = 0
    print("🚀 AI Virtual Mouse Started!")
    
    while True:
        success, img = cap.read()
        if not success or img is None:
            continue
            
        img = cv2.flip(img, 1) # Mirror
        
        # 1. AI Tracking & Visualization
        img = tracker.find_hands(img, draw=True) # Now draws skeleton
        lm_list = tracker.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            x1, y1 = lm_list[8][1], lm_list[8][2] # Index
            x2, y2 = lm_list[12][1], lm_list[12][2] # Middle
            fingers = tracker.fingers_up()
            
            # --- FINGER DASHBOARD (Bottom Left) ---
            names = ["T", "I", "M", "R", "P"]
            for i, status in enumerate(fingers):
                color = (0, 255, 0) if status == 1 else (0, 0, 255)
                cv2.rectangle(img, (20 + i*40, V_HEIGHT-60), (50 + i*40, V_HEIGHT-30), color, cv2.FILLED)
                cv2.putText(img, names[i], (25 + i*40, V_HEIGHT-35), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

            # --- GESTURE LOGIC ---

            # A. MOVE: Index UP only
            if fingers[1] == 1 and fingers[2] == 0:
                mouse.move_cursor(x1, y1, V_WIDTH, V_HEIGHT, margin=FRAME_MARGIN)
                cv2.putText(img, ">>> MOVING", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)

            # B. LEFT CLICK: Index + Middle Pinch
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                dist = np.hypot(x2 - x1, y2 - y1)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 255), 2)
                if dist < 45: 
                    cv2.putText(img, "!!! CLICK !!!", (x1-50, y1-50), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 4)
                    mouse.click()
                    time.sleep(0.1)
                else:
                    cv2.putText(img, "PINCH", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

            # C. RIGHT CLICK: 3 Fingers UP
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                cv2.putText(img, "RIGHT CLICK", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 200, 255), 3)
                mouse.right_click()
                time.sleep(0.3)

            # D. VOLUME: Thumb + Index UP
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                vol = int(np.interp(y1, (50, V_HEIGHT - 50), (100, 0)))
                sys_ctrl.volume_control(vol)
                cv2.putText(img, f"VOL: {vol}%", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

            # E. SCREENSHOT: Thumb + Pinky UP
            elif fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                try:
                    sys_ctrl.take_screenshot()
                    cv2.putText(img, "SAVE SCREENSHOT", (150, 240), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 4)
                    cv2.imshow("AI Virtual Mouse Feed", img)
                    cv2.waitKey(500)
                except: pass

            # F. SCROLL: 4 Fingers UP
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
                direction = "UP" if y1 < V_HEIGHT // 2 else "DOWN"
                mouse.scroll('up' if direction == "UP" else 'down')
                cv2.putText(img, f"SCROLL {direction}", (200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3)

        # 2. Performance & Dashboard
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        stats = perf_mon.get_latest_stats()
        
        # Stats Overlay
        cv2.rectangle(img, (0, 0), (200, 80), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, f"FPS: {int(fps)}", (10, 25), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"CPU: {stats['cpu']}%", (10, 50), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"RAM: {stats['memory']}MB", (10, 75), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        # 3. Final Render
        cv2.imshow("AI Virtual Mouse Feed", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
