
import cv2
import numpy as np
import time
import math
from hand_tracker import HandTracker
from mouse_controller import MouseController
from system_controller import SystemController
from performance_monitor import PerformanceMonitor

def main():
    V_WIDTH, V_HEIGHT = 640, 480
    FRAME_MARGIN = 100
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ CAMERA ERROR: Could not access webcam.")
        return

    cap.set(3, V_WIDTH)
    cap.set(4, V_HEIGHT)
    
    tracker = HandTracker(max_hands=2, detection_con=0.4)
    mouse = MouseController(smoothing=4)
    sys_ctrl = SystemController()
    perf_mon = PerformanceMonitor()
    
    # State Variables
    canvas = np.zeros((V_HEIGHT, V_WIDTH, 3), np.uint8)
    draw_mode = False
    prev_draw_x, prev_draw_y = 0, 0
    prev_draw_x2, prev_draw_y2 = 0, 0
    draw_color = (0, 255, 0) # Default Green
    brush_thickness = 5
    eraser_thickness = 50
    swipe_cooldown = 0
    volume_cooldown = 0
    
    # 2-Hand Statics
    initial_dist = 0
    initial_angle = 0
    zoom_cooldown = 0
    
    p_time = 0
    print("🚀 AI Virtual Mouse Started - HAND ELITE MODE!")
    
    while True:
        success, img = cap.read()
        if not success or img is None:
            continue
            
        img = cv2.flip(img, 1) 
        
        # 1. AI Tracking
        # MediaPipe Video mode requires monotonic timestamps in ms
        timestamp_ms = int(time.time() * 1000)
        img = tracker.find_hands(img, draw=True, timestamp_ms=timestamp_ms)
        
        # Get data for all detected hands
        hands_data = []
        if tracker.results and tracker.results.hand_landmarks:
            for i in range(len(tracker.results.hand_landmarks)):
                lm_list = tracker.find_position(img, hand_no=i, draw=False)
                fingers = tracker.fingers_up(lm_list)
                hands_data.append({'lm': lm_list, 'fingers': fingers})


        
        # 1. Whiteboard UI Rendering (Always show in draw mode)
        if draw_mode:
            cv2.rectangle(img, (0, 0), (100, 70), (255, 0, 0), cv2.FILLED) # Blue
            cv2.rectangle(img, (100, 0), (200, 70), (0, 255, 0), cv2.FILLED) # Green
            cv2.rectangle(img, (200, 0), (300, 70), (0, 0, 255), cv2.FILLED) # Red
            cv2.rectangle(img, (300, 0), (450, 70), (200, 200, 200), cv2.FILLED) # Eraser
            cv2.putText(img, "ERASER", (320, 45), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 3)
            cv2.rectangle(img, (450, 0), (640, 70), (50, 50, 50), cv2.FILLED) # Clear
            cv2.putText(img, "CLEAR", (480, 45), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)

            # Highlight Selected Color
            if draw_color == (255, 0, 0): cv2.rectangle(img, (0,0), (100, 70), (255,255,100), 4)
            elif draw_color == (0, 255, 0): cv2.rectangle(img, (100,0), (200, 70), (255,255,100), 4)
            elif draw_color == (0, 0, 255): cv2.rectangle(img, (200,0), (300, 70), (255,255,100), 4)
            elif draw_color == (0, 0, 0): cv2.rectangle(img, (300,0), (450, 70), (0,255,0), 4)

        # 2. Process Individual Hand Gestures (Looping over all hands)
        for i, data in enumerate(hands_data):
            lm = data['lm']
            fingers = data['fingers']
            x1, y1 = lm[8][1], lm[8][2]
            x2, y2 = lm[12][1], lm[12][2]

            # --- DRAW MODE LOGIC ---
            if draw_mode:
                if fingers[1] == 1:
                    # Header Interaction (Only first hand can change settings to avoid conflict)
                    if i == 0 and y1 < 70:
                        if 0 < x1 < 100: draw_color = (255, 0, 0)
                        elif 100 < x1 < 200: draw_color = (0, 255, 0)
                        elif 200 < x1 < 300: draw_color = (0, 0, 255)
                        elif 300 < x1 < 450: draw_color = (0, 0, 0)
                        elif 450 < x1 < 640: canvas = np.zeros((V_HEIGHT, V_WIDTH, 3), np.uint8)
                    
                    # Drawing (Both hands can draw smoothly!)
                    elif y1 > 70:
                        thickness = brush_thickness if draw_color != (0, 0, 0) else eraser_thickness
                        if i == 0:
                            if prev_draw_x == 0: prev_draw_x, prev_draw_y = x1, y1
                            cv2.line(canvas, (prev_draw_x, prev_draw_y), (x1, y1), draw_color, thickness)
                            prev_draw_x, prev_draw_y = x1, y1
                        else:
                            if prev_draw_x2 == 0: prev_draw_x2, prev_draw_y2 = x1, y1
                            cv2.line(canvas, (prev_draw_x2, prev_draw_y2), (x1, y1), draw_color, thickness)
                            prev_draw_x2, prev_draw_y2 = x1, y1
                        
                        cv2.circle(img, (x1, y1), 8, draw_color, cv2.FILLED)
                else:
                    if i == 0: prev_draw_x, prev_draw_y = 0, 0
                    else: prev_draw_x2, prev_draw_y2 = 0, 0

            # --- NAVIGATION & SYSTEM MODE ---
            else:
                if fingers == [0, 0, 0, 0, 0]: # Reset/Pause
                    if swipe_cooldown == 0: sys_ctrl.media_control('play_pause'); swipe_cooldown = 40
                
                elif fingers == [1, 0, 0, 0, 0]: # App Switcher
                    if swipe_cooldown == 0: sys_ctrl.app_switcher(); swipe_cooldown = 20

                elif fingers == [1, 1, 0, 0, 0]: # Volume Control
                    if volume_cooldown == 0:
                        if y1 < 200: sys_ctrl.volume_step('up')
                        elif y1 > 300: sys_ctrl.volume_step('down')
                        volume_cooldown = 5

                # Pinky UP to toggle draw mode
                if fingers == [0, 0, 0, 0, 1] and swipe_cooldown == 0:
                    draw_mode = not draw_mode
                    swipe_cooldown = 30

                # Mouse Control (Only first hand controls cursor)
                if i == 0:
                    if fingers[1] == 1 and fingers[2] == 0:
                        mouse.move_cursor(x1, y1, V_WIDTH, V_HEIGHT, margin=FRAME_MARGIN)
                    elif fingers[1] == 1 and fingers[2] == 1 and np.hypot(x2-x1, y2-y1) < 45:
                        mouse.click()
                    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1:
                        mouse.right_click()

        # 3. Two-Hand Special Gestures (Zoom & Rotate)
        if len(hands_data) == 2:
            h1, h2 = hands_data[0]['lm'], hands_data[1]['lm']
            cx1, cy1 = h1[9][1], h1[9][2]
            cx2, cy2 = h2[9][1], h2[9][2]
            
            curr_dist = np.hypot(cx2 - cx1, cy2 - cy1)
            curr_angle = math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))
            
            if initial_dist == 0:
                initial_dist, initial_angle = curr_dist, curr_angle
            else:
                dist_diff = curr_dist - initial_dist
                if abs(dist_diff) > 50 and zoom_cooldown == 0:
                    if dist_diff > 0: sys_ctrl.zoom_control('in')
                    else: sys_ctrl.zoom_control('out')
                    zoom_cooldown = 10
                    initial_dist = curr_dist
                
                angle_diff = curr_angle - initial_angle
                if abs(angle_diff) > 20 and zoom_cooldown == 0:
                    if angle_diff > 0: sys_ctrl.rotate_control('right')
                    else: sys_ctrl.rotate_control('left')
                    zoom_cooldown = 15
                    initial_angle = curr_angle

            cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 255), 3)
            cv2.putText(img, "MULTI-HAND ACTIVE", (200, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
        else:
            initial_dist = 0

        # Merge & Render
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, img_inv)
        img = cv2.bitwise_or(img, canvas)

        if swipe_cooldown > 0: swipe_cooldown -= 1
        if volume_cooldown > 0: volume_cooldown -= 1
        if zoom_cooldown > 0: zoom_cooldown -= 1

        # Perf
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        stats = perf_mon.get_latest_stats()
        cv2.rectangle(img, (0, 0), (200, 80), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, f"FPS: {int(fps)} | M-HAND: {len(hands_data)}", (10, 25), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        cv2.putText(img, f"CPU: {stats['cpu']}% RAM: {stats['memory']}MB", (10, 55), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        
        # --- FINGER STATUS DISPLAY (T I M R P) ---
        for i, data in enumerate(hands_data):
            fingers = data['fingers']
            labels = ['T', 'I', 'M', 'R', 'P']
            # Position at bottom: Hand 1 on left, Hand 2 on right
            x_start = 20 + (i * 200)
            y_pos = V_HEIGHT - 20
            cv2.putText(img, f"H{i+1}:", (x_start, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 255, 255), 2)
            for j, status in enumerate(fingers):
                color = (0, 255, 0) if status == 1 else (0, 0, 255) # Green if Up, Red if Down
                cv2.putText(img, labels[j], (x_start + 45 + j * 25, y_pos), cv2.FONT_HERSHEY_PLAIN, 1.2, color, 2)

        cv2.imshow("AI Virtual Mouse Feed", img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
