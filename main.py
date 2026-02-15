import cv2
import numpy as np
import customtkinter as ctk
import time
from hand_tracker import HandTracker
from mouse_controller import MouseController
from system_controller import SystemController
from performance_monitor import PerformanceMonitor

class VirtualMouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # --- UI Setup ---
        self.title("AI Virtual Mouse - Pro Controller")
        self.geometry("900x600")
        ctk.set_appearance_mode("dark")
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar for settings
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="AI Controller", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(pady=20)
        
        self.smooth_label = ctk.CTkLabel(self.sidebar, text="Mouse Smoothing")
        self.smooth_label.pack(pady=(10, 0))
        self.smooth_slider = ctk.CTkSlider(self.sidebar, from_=1, to=20, command=self.update_smoothing)
        self.smooth_slider.set(7)
        self.smooth_slider.pack(pady=10)
        
        self.conf_label = ctk.CTkLabel(self.sidebar, text="Detection Confidence")
        self.conf_label.pack(pady=(10, 0))
        self.conf_slider = ctk.CTkSlider(self.sidebar, from_=0.1, to=1.0, command=self.update_confidence)
        self.conf_slider.set(0.8)
        self.conf_slider.pack(pady=10)
        
        self.stats_label = ctk.CTkLabel(self.sidebar, text="System Stats", font=ctk.CTkFont(weight="bold"))
        self.stats_label.pack(pady=(30, 10))
        
        self.perf_text = ctk.CTkLabel(self.sidebar, text="CPU: 0% | RAM: 0MB\nFPS: 0", justify="left")
        self.perf_text.pack(pady=5)

        # Main Area for Info
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.info_box = ctk.CTkTextbox(self.main_frame, width=500, height=400)
        self.info_box.pack(pady=20, padx=20, fill="both", expand=True)
        self.info_box.insert("0.0", "🚀 AI Virtual Mouse is Running!\n\n"
                                     "GESTURES GUIDE:\n"
                                     "-----------------\n"
                                     "📍 Move Mouse: Index Finger Up\n"
                                     "🖱️ Left Click: Index + Middle Pinch\n"
                                     "🖱️ Right Click: Index + Middle + Ring Up\n"
                                     "📜 Scroll: 4 Fingers Up (Move Hand Up/Down)\n"
                                     "🔊 Volume: Thumb + Index (Vertical Height)\n"
                                     "📸 Screenshot: Thumb + Pinky\n\n"
                                     "Controls:\n"
                                     "- Press 'q' on the Video window to stop tracking\n"
                                     "- Use sliders on the left to calibrate in real-time.")
        self.info_box.configure(state="disabled")


        self.v_width, self.v_height = 640, 480
        self.cap = cv2.VideoCapture(0)

        initial_conf = self.conf_slider.get()
        self.tracker = HandTracker(max_hands=1, detection_con=initial_conf)
        self.mouse = MouseController(smoothing=int(self.smooth_slider.get()))
        self.sys_ctrl = SystemController()
        self.perf_mon = PerformanceMonitor()
        self.perf_mon.start()
        
        self.p_time = 0
        self.is_running = True
        
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("❌ Error: Camera could not be opened. Check Permissions.")
            self.info_box.configure(state="normal")
            self.info_box.insert("end", "\n\n⚠️ CAMERA ERROR: Could not access webcam. Please check System Settings > Privacy & Security > Camera.")
            self.info_box.configure(state="disabled")
        
        # Start the processing loop
        try:
            self.process_camera()
        except Exception as e:
            print(f"❌ Startup Error: {e}")

    def update_smoothing(self, value):
        self.mouse.smoothing = int(value)

    def update_confidence(self, value):
        try:
            self.tracker = HandTracker(max_hands=1, detection_con=float(value))
        except Exception as e:
            print(f"❌ Error updating confidence: {e}")

    def process_camera(self):
        if not self.is_running:
            return

        try:
            success, img = self.cap.read()
            if success:
                img = cv2.flip(img, 1)
                img = self.tracker.find_hands(img)
                lm_list = self.tracker.find_position(img, draw=False)
                
                if len(lm_list) != 0:
                    x1, y1 = lm_list[8][1], lm_list[8][2]
                    x2, y2 = lm_list[12][1], lm_list[12][2]
                    fingers = self.tracker.fingers_up()
                    
                    if fingers[1] == 1 and fingers[2] == 0:
                        self.mouse.move_cursor(x1, y1, self.v_width, self.v_height)
                        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
    
                    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0:
                        dist = np.hypot(x2 - x1, y2 - y1)
                        if dist < 40:
                            cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                            self.mouse.click()
                            time.sleep(0.1)
                    
                    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
                        self.mouse.right_click()
                        time.sleep(0.3)
                    
                    elif fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:
                        vol_level = int(np.interp(y1, (50, self.v_height - 50), (100, 0)))
                        self.sys_ctrl.volume_control(vol_level)
                        cv2.putText(img, f"Vol: {vol_level}", (450, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
    
                    elif fingers[0] == 1 and fingers[4] == 1 and fingers[1] == 0:
                        self.sys_ctrl.take_screenshot()
                        cv2.putText(img, "Screenshot!", (200, 240), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                        time.sleep(0.5)
    
                    elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1 and fingers[0] == 0:
                        if y1 < self.v_height // 2:
                            self.mouse.scroll('up')
                        else:
                            self.mouse.scroll('down')
    
                c_time = time.time()
                fps = 1 / (c_time - self.p_time) if (c_time - self.p_time) > 0 else 0
                self.p_time = c_time
                
                stats = self.perf_mon.get_latest_stats()
                self.perf_text.configure(text=f"CPU: {stats['cpu']}% | RAM: {int(stats['memory'])}MB\nFPS: {int(fps)}")
                
                cv2.putText(img, f"FPS: {int(fps)}", (20, 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), 2)
                cv2.imshow("AI Virtual Mouse Feed", img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop_app()
                    return
            else:
                # If camera fails, show notice in the UI instead of crashing
                self.perf_text.configure(text="Camera Error!\nCheck Permissions")

        except Exception as e:
            print(f"❌ Core Loop Error: {e}")

        # Always keep the window alive
        self.after(5, self.process_camera)

    def stop_app(self):
        self.is_running = False
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.perf_mon.stop()
        self.destroy()

if __name__ == "__main__":
    try:
        app = VirtualMouseApp()
        app.mainloop()
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
