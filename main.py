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
    
    # Drawing Canvas
    canvas = np.zeros((V_HEIGHT, V_WIDTH, 3), np.uint8)
    draw_mode = False
    prev_draw_x, prev_draw_y = 0, 0
    
    # Swipe Detection
    prev_palm_x = 0
    swipe_cooldown = 0
    
    p_time = 0
    print("🚀 AI Virtual Mouse Started - ADVANCED MODE!")
    
    while True:
        success, img = cap.read()
        if not success or img is None:
            continue
            
        img = cv2.flip(img, 1) # Mirror
        
        # 1. AI Tracking
        img = tracker.find_hands(img, draw=True)
        lm_list = tracker.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            x1, y1 = lm_list[8][1], lm_list[8][2]    # Index
            x2, y2 = lm_list[12][1], lm_list[12][2]  # Middle
            wrist_x = lm_list[0][1]                  # Wrist for swipe
            fingers = tracker.fingers_up()
            
            # --- FINGER DASHBOARD ---
            names = ["T", "I", "M", "R", "P"]
            for i, status in enumerate(fingers):
                color = (0, 255, 0) if status == 1 else (0, 0, 255)
                cv2.rectangle(img, (20 + i*40, V_HEIGHT-60), (50 + i*40, V_HEIGHT-30), color, cv2.FILLED)
                cv2.putText(img, names[i], (25 + i*40, V_HEIGHT-35), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

            # --- GESTURE LOGIC ---

            # 1. APP SWITCHER: Thumb UP only
            if fingers == [1, 0, 0, 0, 0]:
                if swipe_cooldown == 0:
                    sys_ctrl.app_switcher()
                    swipe_cooldown = 20
                cv2.putText(img, "APP SWITCH", (x1, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 3)

            # 2. WHITEBOARD TOGGLE: Pinky UP only
            elif fingers == [0, 0, 0, 0, 1]:
                if swipe_cooldown == 0:
                    draw_mode = not draw_mode
                    swipe_cooldown = 30
                mode_str = "ON" if draw_mode else "OFF"
                cv2.putText(img, f"WHITEBOARD: {mode_str}", (150, 240), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

            # 3. BROWSER SWIPE: 5 Fingers UP
            elif fingers == [1, 1, 1, 1, 1]:
                if prev_palm_x != 0 and swipe_cooldown == 0:
                    diff = wrist_x - prev_palm_x
                    if diff > 50: # Fast Right
                        sys_ctrl.browser_nav("forward")
                        swipe_cooldown = 15
                        print("Browser Forward")
                    elif diff < -50: # Fast Left
                        sys_ctrl.browser_nav("back")
                        swipe_cooldown = 15
                        print("Browser Back")
                prev_palm_x = wrist_x
                cv2.putText(img, "NAV MODE", (200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3)
            else:
                prev_palm_x = 0

            # 4. DRAWING / MOUSE INPUT
            if draw_mode:
                if fingers[1] == 1: # Index up to draw
                    cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                    if prev_draw_x == 0:
                        prev_draw_x, prev_draw_y = x1, y1
                    cv2.line(canvas, (prev_draw_x, prev_draw_y), (x1, y1), (0, 255, 0), 5)
                    prev_draw_x, prev_draw_y = x1, y1
                else:
                    prev_draw_x, prev_draw_y = 0, 0
                
                # Clear Canvas: Index + Middle Pinch
                if fingers[1] == 1 and fingers[2] == 1:
                    dist = np.hypot(x2 - x1, y2 - y1)
                    if dist < 40:
                        canvas = np.zeros((V_HEIGHT, V_WIDTH, 3), np.uint8)
                        cv2.putText(img, "CLEARED", (x1, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
            else:
                # NORMAL MOUSE OPERATIONS
                if fingers[1] == 1 and fingers[2] == 0:
                    mouse.move_cursor(x1, y1, V_WIDTH, V_HEIGHT, margin=FRAME_MARGIN)
                    cv2.putText(img, "MOVING", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
                elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                    if np.hypot(x2 - x1, y2 - y1) < 45:
                        mouse.click()
                        time.sleep(0.1)

            # E. VOLUME: Thumb + Index
            if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                vol = int(np.interp(y1, (50, V_HEIGHT - 50), (100, 0)))
                sys_ctrl.volume_control(vol)

        # Merge Canvas with Video feed
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, canvas)

        if swipe_cooldown > 0:
            swipe_cooldown -= 1

        # Stats
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        stats = perf_mon.get_latest_stats()
        cv2.rectangle(img, (0, 0), (200, 80), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, f"FPS: {int(fps)}", (10, 25), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"WHITEBOARD: {'ON' if draw_mode else 'OFF'}", (220, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        cv2.imshow("AI Virtual Mouse Feed", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
