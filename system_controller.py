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

    def media_control(self, action):
        """
        action: 'play_pause', 'mute'
        """
        try:
            if action == 'play_pause':
                pyautogui.press('space')
            elif action == 'mute':
                pyautogui.press('mute') # This might vary by system/app, but 'mute' is standard for OS
                # Alternatively for YouTube:
                # pyautogui.press('m')
        except Exception as e:
            print(f"Media Control Error: {e}")

    def zoom_control(self, direction):
        """
        direction: 'in', 'out'
        """
        try:
            if direction == 'in':
                pyautogui.hotkey('command', '+')
            else:
                pyautogui.hotkey('command', '-')
        except Exception as e:
            print(f"Zoom Error: {e}")

    def rotate_control(self, direction):
        """
        direction: 'left', 'right'
        """
        try:
            if direction == 'left':
                pyautogui.hotkey('command', 'l') # Common shortcut for rotate left
            else:
                pyautogui.hotkey('command', 'r') # Common shortcut for rotate right
        except Exception as e:
            print(f"Rotate Error: {e}")

    def take_screenshot(self):
        try:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            save_path = os.path.join(self.desktop_path, f"AI_Screenshot_{timestamp}.png")
            os.system(f"screencapture '{save_path}'")
            print(f"📸 Screenshot saved to Desktop: {save_path}")
        except Exception as e:
            print(f"❌ Screenshot Error: {e}")

    def browser_nav(self, direction):
        try:
            if direction == "back":
                pyautogui.hotkey('command', 'left')
            else:
                pyautogui.hotkey('command', 'right')
        except Exception as e:
            print(f"Browser Nav Error: {e}")

    def app_switcher(self):
        try:
            pyautogui.hotkey('command', 'tab')
        except Exception as e:
            print(f"App Switcher Error: {e}")

    def app_launcher(self, app_name):
        try:
            os.system(f"open -a '{app_name}'")
        except Exception as e:
            print(f"App Launcher Error: {e}")
