import customtkinter as ctk

class GesterUI(ctk.CTk):
    def __init__(self, settings_callback=None):
        super().__init__()
        
        self.settings_callback = settings_callback
        
        self.title("AI Virtual Mouse Settings")
        self.geometry("400x500")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.label = ctk.CTkLabel(self, text="Mouse Settings", font=("Roboto", 24, "bold"))
        self.label.pack(pady=20)
        
        self.smoothing_label = ctk.CTkLabel(self, text="Smoothing (Lower = Faster)")
        self.smoothing_label.pack(pady=5)
        self.smoothing_slider = ctk.CTkSlider(self, from_=1, to=15, command=self.update_settings)
        self.smoothing_slider.set(7)
        self.smoothing_slider.pack(pady=10)
        
        self.det_label = ctk.CTkLabel(self, text="Detection Confidence")
        self.det_label.pack(pady=5)
        self.det_slider = ctk.CTkSlider(self, from_=0.1, to=1.0, command=self.update_settings)
        self.det_slider.set(0.8)
        self.det_slider.pack(pady=10)
        
        self.info_box = ctk.CTkTextbox(self, width=350, height=150)
        self.info_box.pack(pady=20)
        self.info_box.insert("0.0", "Gestures Guide:\n\n"
                                     "- Index Finger: Move Cursor\n"
                                     "- Index + Middle (Pinch): Left Click\n"
                                     "- Index + Middle + Ring: Right Click\n"
                                     "- All 4 Fingers: Scroll (Up/Down based on Y)\n"
                                     "- Thumb + Index: Volume Control\n"
                                     "- Thumb + Pinky: Screenshot\n"
                                     "- 'q' on Video window: Quit")
        self.info_box.configure(state="disabled")

    def update_settings(self, _=None):
        if self.settings_callback:
            settings = {
                "smoothing": int(self.smoothing_slider.get()),
                "detection_con": self.det_slider.get()
            }
            self.settings_callback(settings)

def start_ui(callback):
    app = GesterUI(settings_callback=callback)
    app.mainloop()

if __name__ == "__main__":
    start_ui(lambda x: print(x))
