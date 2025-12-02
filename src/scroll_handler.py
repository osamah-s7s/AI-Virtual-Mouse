"""
Scroll handler with progressive speed control.
Manages scroll state and calculates scroll speeds based on hand position.
"""

import math
import time
from .config import (
    CAMERA_HEIGHT, BASE_SCROLL_SENSITIVITY, MAX_SCROLL_SENSITIVITY,
    SCROLL_DELAY, SCROLL_HISTORY_LENGTH, SCROLL_BOOST_MULTIPLIER,
    SCROLL_NEUTRAL_ZONE_HEIGHT_RATIO
)


class ScrollHandler:
    """
    Handles scroll operations with progressive speed and smoothing.
    """
    
    def __init__(self):
        """Initialize scroll handler with default state."""
        self.scroll_mode = False
        self.scroll_history = []
        self.last_scroll_time = 0
        self.history_length = SCROLL_HISTORY_LENGTH
    
    def smooth_scroll(self, current_amount):
        """
        Apply smoothing to scroll amount using moving average.
        
        Args:
            current_amount: Current scroll amount
        
        Returns:
            Smoothed scroll amount
        """
        self.scroll_history.append(current_amount)
        if len(self.scroll_history) > self.history_length:
            self.scroll_history.pop(0)
        return sum(self.scroll_history) / len(self.scroll_history)
    
    def get_progressive_speed(self, y_pos):
        """
        Calculate scroll speed based on hand position with balanced zones.
        
        Args:
            y_pos: Y position of hand in camera frame
        
        Returns:
            Scroll speed (negative for up, positive for down, 0 for neutral)
        """
        # Define the neutral zone in the center (no scrolling)
        neutral_zone_height = int(CAMERA_HEIGHT * SCROLL_NEUTRAL_ZONE_HEIGHT_RATIO)
        neutral_top = (CAMERA_HEIGHT - neutral_zone_height) // 2
        neutral_bottom = (CAMERA_HEIGHT + neutral_zone_height) // 2
        
        # Check if in neutral zone
        if neutral_top <= y_pos <= neutral_bottom:
            return 0
        
        # Calculate speed for top zone (scrolling up)
        if y_pos < neutral_top:
            # Normalized distance from neutral edge (0 to 1)
            dist_from_neutral = (neutral_top - y_pos) / neutral_top
            # Apply exponential curve for progressive speed
            speed_factor = math.pow(dist_from_neutral, 2)  # Quadratic curve
            return -(BASE_SCROLL_SENSITIVITY) + (MAX_SCROLL_SENSITIVITY - BASE_SCROLL_SENSITIVITY) * speed_factor
        
        # Calculate speed for bottom zone (scrolling down)
        else:
            # Normalized distance from neutral edge (0 to 1)
            dist_from_neutral = (y_pos - neutral_bottom) / (CAMERA_HEIGHT - neutral_bottom)
            # Apply exponential curve for progressive speed
            speed_factor = math.pow(dist_from_neutral, 2)  # Quadratic curve
            return BASE_SCROLL_SENSITIVITY + (MAX_SCROLL_SENSITIVITY - BASE_SCROLL_SENSITIVITY) * speed_factor
    
    def get_scroll_zones(self):
        """
        Get scroll zone boundaries for visualization.
        
        Returns:
            tuple: (neutral_top, neutral_bottom, neutral_zone_height)
        """
        neutral_zone_height = int(CAMERA_HEIGHT * SCROLL_NEUTRAL_ZONE_HEIGHT_RATIO)
        neutral_top = (CAMERA_HEIGHT - neutral_zone_height) // 2
        neutral_bottom = (CAMERA_HEIGHT + neutral_zone_height) // 2
        return neutral_top, neutral_bottom, neutral_zone_height
    
    def should_scroll(self, scroll_speed):
        """
        Check if scroll should be performed based on timing and speed.
        
        Args:
            scroll_speed: Calculated scroll speed
        
        Returns:
            True if scroll should be performed
        """
        current_time = time.time()
        return (current_time - self.last_scroll_time > SCROLL_DELAY and 
                abs(scroll_speed) > 0.5)
    
    def update_scroll_time(self):
        """Update the last scroll time to current time."""
        self.last_scroll_time = time.time()
    
    def activate_scroll_mode(self):
        """Activate scroll mode and reset history."""
        self.scroll_mode = True
        self.scroll_history = []
    
    def deactivate_scroll_mode(self):
        """Deactivate scroll mode."""
        self.scroll_mode = False
    
    def is_scroll_mode_active(self):
        """
        Check if scroll mode is active.
        
        Returns:
            True if scroll mode is active
        """
        return self.scroll_mode

