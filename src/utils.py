"""
Utility functions for FPS calculation and visual feedback.
"""

import cv2
import time
from .config import (
    FPS_DISPLAY_POSITION, FPS_FONT_SCALE, FPS_COLOR, FPS_THICKNESS
)


class FPSCounter:
    """
    FPS counter for measuring and displaying frame rate.
    """
    
    def __init__(self):
        """Initialize FPS counter."""
        self.prev_time = 0
    
    def update(self):
        """
        Update FPS calculation and return current FPS.
        
        Returns:
            Current FPS value
        """
        current_time = time.time()
        if self.prev_time == 0:
            self.prev_time = current_time
            return 0
        
        fps = 1 / (current_time - self.prev_time)
        self.prev_time = current_time
        return fps
    
    def draw_fps(self, img, fps):
        """
        Draw FPS on image.
        
        Args:
            img: Image to draw on
            fps: FPS value to display
        
        Returns:
            Image with FPS text
        """
        cv2.putText(img, f'FPS: {int(fps)}', FPS_DISPLAY_POSITION,
                   cv2.FONT_HERSHEY_PLAIN, FPS_FONT_SCALE, FPS_COLOR, FPS_THICKNESS)
        return img

