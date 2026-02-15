import pyautogui
import numpy as np
from screeninfo import get_monitors

class MouseController:
    def __init__(self, smoothing=4):
        self.smoothing = smoothing
        self.ploc_x, self.ploc_y = 0, 0
        self.cloc_x, self.cloc_y = 0, 0
        
        monitor = get_monitors()[0]
        self.screen_width = monitor.width
        self.screen_height = monitor.height
        
   
        pyautogui.PAUSE = 0
        pyautogui.MINIMUM_DURATION = 0
        pyautogui.MINIMUM_SLEEP = 0
        pyautogui.FAILSAFE = False

    def move_cursor(self, x, y, frame_w, frame_h, margin=100):
        x_mapped = np.interp(x, (margin, frame_w - margin), (0, self.screen_width))
        y_mapped = np.interp(y, (margin, frame_h - margin), (0, self.screen_height))
        

        dist = np.hypot(x_mapped - self.ploc_x, y_mapped - self.ploc_y)
        dynamic_smoothing = self.smoothing
        if dist < 10:
            dynamic_smoothing = self.smoothing * 1.5 # Extra smooth for fine control
        elif dist > 100:
            dynamic_smoothing = max(2, self.smoothing / 2) # Faster for big jumps
            
        self.cloc_x = self.ploc_x + (x_mapped - self.ploc_x) / dynamic_smoothing
        self.cloc_y = self.ploc_y + (y_mapped - self.ploc_y) / dynamic_smoothing
        
        pyautogui.moveTo(self.cloc_x, self.cloc_y)
        self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y

    def click(self, button='left'):
        pyautogui.click(button=button)

    def double_click(self):
        pyautogui.doubleClick()

    def scroll(self, direction):

        amount = 5 if direction == 'up' else -5
        pyautogui.scroll(amount)

    def right_click(self):
        pyautogui.click(button='right')
