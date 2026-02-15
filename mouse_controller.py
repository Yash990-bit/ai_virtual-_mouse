import pyautogui
import numpy as np
from screeninfo import get_monitors

class MouseController:
    def __init__(self, smoothing=5):
        self.smoothing = smoothing
        self.ploc_x, self.ploc_y = 0, 0
        self.cloc_x, self.cloc_y = 0, 0
        
        # Get screen dimensions
        monitor = get_monitors()[0]
        self.screen_width = monitor.width
        self.screen_height = monitor.height
        
        # Disable PyAutoGUI fail-safe for smoother movement (use with caution)
        pyautogui.FAILSAFE = False

    def move_cursor(self, x, y, frame_w, frame_h, margin=100):
        # Map frame coordinates to screen coordinates with a margin
        # This allows the user to reach the edges of the screen more easily
        x_mapped = np.interp(x, (margin, frame_w - margin), (0, self.screen_width))
        y_mapped = np.interp(y, (margin, frame_h - margin), (0, self.screen_height))
        
        # Smoothing logic
        self.cloc_x = self.ploc_x + (x_mapped - self.ploc_x) / self.smoothing
        self.cloc_y = self.ploc_y + (y_mapped - self.ploc_y) / self.smoothing
        
        # Move the mouse
        pyautogui.moveTo(self.screen_width - self.cloc_x, self.cloc_y)
        self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y

    def click(self, button='left'):
        pyautogui.click(button=button)

    def double_click(self):
        pyautogui.doubleClick()

    def scroll(self, direction):
        # direction: 'up' or 'down'
        amount = 5 if direction == 'up' else -5
        pyautogui.scroll(amount)

    def right_click(self):
        pyautogui.click(button='right')
