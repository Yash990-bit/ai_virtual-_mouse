import cv2
import numpy as np
import time
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
    
    tracker = HandTracker(max_hands=1, detection_con=0.7)
    mouse = MouseController(smoothing=7)
    sys_ctrl = SystemController()
    perf_mon = PerformanceMonitor()
    
    p_time = 0
    print("🚀 AI Virtual Mouse Started!")
    print("📍 Press 'q' on the Video window to Quit.")
    
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read camera feed.")
            break
            
        img = cv2.flip(img, 1) 
        
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img, draw=False)
        
        if len(lm_list) != 0:
            
            x1, y1 = lm_list[8][1], lm_list[8][2]
            x2, y2 = lm_list[12][1], lm_list[12][2]
            fingers = tracker.fingers_up()
            


            if fingers[1] == 1 and fingers[2] == 0:
                mouse.move_cursor(x1, y1, V_WIDTH, V_HEIGHT, margin=FRAME_MARGIN)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                cv2.putText(img, "Moving", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                dist = np.hypot(x2 - x1, y2 - y1)
                if dist < 40:
                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, "CLICK!", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                    mouse.click()
                    time.sleep(0.1)

            # C. RIGHT CLICK: 3 Fingers Up
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                cv2.putText(img, "RIGHT CLICK", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
                mouse.right_click()
                time.sleep(0.3)

            # D. VOLUME CONTROL: Thumb + Index
            elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                vol_level = int(np.interp(y1, (50, V_HEIGHT - 50), (100, 0)))
                sys_ctrl.volume_control(vol_level)
                cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
                cv2.rectangle(img, (50, int(np.interp(vol_level, [0, 100], [400, 150]))), (85, 400), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f"VOL: {vol_level}%", (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
            
            # E. SCREENSHOT: Thumb + Pinky
            elif fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                try:
                    sys_ctrl.take_screenshot()
                    cv2.putText(img, "SCREENSHOT!", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                    cv2.imshow("AI Virtual Mouse Feed", img)
                    cv2.waitKey(500) # Freeze for a moment to show capture
                except Exception as e:
                    print(f"Main Loop Screenshot Error: {e}")

            # F. SCROLL: 4 Fingers Up
            elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and fingers[0] == 0:
                if y1 < V_HEIGHT // 2:
                    mouse.scroll('up')
                    cv2.putText(img, "SCROLL UP", (250, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
                else:
                    mouse.scroll('down')
                    cv2.putText(img, "SCROLL DOWN", (250, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

        # 2. Performance Stats
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        stats = perf_mon.get_latest_stats()
        
        # Display Stats Overlay
        cv2.rectangle(img, (10, 10), (250, 100), (0, 0, 0), cv2.FILLED)
        cv2.putText(img, f"FPS: {int(fps)}", (20, 35), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"CPU: {stats['cpu']}%", (20, 65), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f"RAM: {stats['memory']}MB", (20, 95), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

        # 3. Render Window
        cv2.imshow("AI Virtual Mouse Feed", img)
        
        # 4. Exit Check
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    print("Project Closed Successfully.")

if __name__ == "__main__":
    main()
