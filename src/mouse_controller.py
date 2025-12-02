"""
Mouse control utilities.
Wraps autopy and pyautogui for mouse operations.
"""

import autopy
import pyautogui


class MouseController:
    """
    Controller for mouse operations.
    Handles movement, clicks, drag, and scroll.
    """
    
    def __init__(self):
        """Initialize mouse controller and get screen dimensions."""
        self.w_screen, self.h_screen = autopy.screen.size()
    
    def move(self, x, y):
        """
        Move mouse to screen coordinates.
        Note: x-coordinate is flipped to mirror camera view.
        
        Args:
            x: Screen X coordinate
            y: Screen Y coordinate
        """
        autopy.mouse.move(self.w_screen - x, y)
    
    def click(self):
        """Perform a left mouse click."""
        autopy.mouse.click()
    
    def right_click(self):
        """Perform a right mouse click."""
        autopy.mouse.click(autopy.mouse.Button.RIGHT)
    
    def toggle_drag(self, state):
        """
        Toggle mouse drag state.
        
        Args:
            state: True to start dragging, False to stop
        """
        autopy.mouse.toggle(autopy.mouse.Button.LEFT, state)
    
    def scroll(self, amount):
        """
        Scroll the mouse wheel.
        
        Args:
            amount: Scroll amount (positive for down, negative for up)
        """
        pyautogui.scroll(amount)
    
    def get_screen_size(self):
        """
        Get screen dimensions.
        
        Returns:
            tuple: (width, height)
        """
        return self.w_screen, self.h_screen

