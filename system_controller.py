import os
import pyautogui
import numpy as np

class SystemController:
    def __init__(self):
        # We can add more system-specific logic here if needed
        pass

    def volume_control(self, level):
        # level is expected to be a value between 0 and 100
        # On macOS, we can use os.system with osascript
        # On Windows, we'd use something else like pycaw
        # For cross-platform, pyautogui can sometimes work but it's limited to volume up/down keys
        
        # Using AppleScript for macOS as per the user's OS
        os.system(f"osascript -e 'set volume output volume {level}'")

    def take_screenshot(self, save_path="screenshot.png"):
        pyautogui.screenshot(save_path)
        print(f"Screenshot saved to {save_path}")

    def app_launcher(self, app_name):
        # Opens an app on macOS
        os.system(f"open -a '{app_name}'")
