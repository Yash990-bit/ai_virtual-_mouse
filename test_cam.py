import cv2
from hand_tracker import HandTracker
import time

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    p_time = 0
    
    print("Running Barebones Test. Press 'q' to quit.")
    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read camera")
            break
            
        img = tracker.find_hands(img)
        lm_list = tracker.find_position(img)
        
        c_time = time.time()
        fps = 1 / (c_time - p_time) if (c_time - p_time) > 0 else 0
        p_time = c_time
        
        cv2.putText(img, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
        cv2.imshow("Test", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
