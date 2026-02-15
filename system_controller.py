import os
import pyautogui
import numpy as np

class SystemController:
    def __init__(self):
        pass

    def volume_control(self, level):
        os.system(f"osascript -e 'set volume output volume {level}'")

    def take_screenshot(self, save_path="screenshot.png"):
        pyautogui.screenshot(save_path)
        print(f"Screenshot saved to {save_path}")

    def app_launcher(self, app_name):
        os.system(f"open -a '{app_name}'")
