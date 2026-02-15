import os
import time
import pyautogui

class SystemController:
    def __init__(self):
        # Determine the Desktop path for saving screenshots
        self.desktop_path = os.path.expanduser("~/Desktop")

    def volume_control(self, level):
        try:
            os.system(f"osascript -e 'set volume output volume {level}'")
        except Exception as e:
            print(f"Volume Control Error: {e}")

    def take_screenshot(self):
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            save_path = os.path.join(self.desktop_path, f"AI_Screenshot_{timestamp}.png")
            os.system(f"screencapture '{save_path}'")
            print(f"📸 Screenshot saved to Desktop: {save_path}")
        except Exception as e:
            print(f"❌ Screenshot Error: {e}")

    # NEW: Browser Navigation
    def browser_nav(self, direction):
        try:
            if direction == "back":
                # Command + Left Arrow for Back
                pyautogui.hotkey('command', 'left')
            else:
                # Command + Right Arrow for Forward
                pyautogui.hotkey('command', 'right')
        except Exception as e:
            print(f"Browser Nav Error: {e}")

    # NEW: App Switcher
    def app_switcher(self):
        try:
            # Command + Tab
            pyautogui.hotkey('command', 'tab')
        except Exception as e:
            print(f"App Switcher Error: {e}")

    def app_launcher(self, app_name):
        try:
            os.system(f"open -a '{app_name}'")
        except Exception as e:
            print(f"App Launcher Error: {e}")
