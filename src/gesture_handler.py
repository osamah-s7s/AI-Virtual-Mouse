"""
Gesture handler for processing hand gestures and controlling mouse.
Main logic for gesture recognition and mouse control.
"""

import cv2
import numpy as np
import time
from .config import (
    CAMERA_WIDTH, CAMERA_HEIGHT, FRAME_REDUCTION, SMOOTHENING,
    DRAG_CLICK_THRESHOLD, PINCH_DISTANCE_THRESHOLD,
    COLOR_MOVE_POINTER, COLOR_LEFT_CLICK, COLOR_RIGHT_CLICK,
    COLOR_FRAME_BOUNDARY, SCROLL_BOOST_MULTIPLIER
)
from .scroll_handler import ScrollHandler


class GestureHandler:
    """
    Handles gesture recognition and mouse control.
    Processes hand landmarks and executes appropriate mouse actions.
    """
    
    def __init__(self, detector, mouse_controller):
        """
        Initialize gesture handler.
        
        Args:
            detector: HandDetector instance
            mouse_controller: MouseController instance
        """
        self.detector = detector
        self.mouse_controller = mouse_controller
        self.scroll_handler = ScrollHandler()
        
        # Cursor smoothing state
        self.ploc_x = 0
        self.ploc_y = 0
        self.cloc_x = 0
        self.cloc_y = 0
        
        # Drag state
        self.drag_mode = False
        self.drag_active = False
        self.drag_start_time = 0
        
        # Screen dimensions
        self.w_screen, self.h_screen = mouse_controller.get_screen_size()
    
    def process_frame(self, img, lm_list, fingers):
        """
        Process a single frame and execute gestures.
        
        Args:
            img: Current frame image
            lm_list: List of hand landmarks
            fingers: List of finger states [thumb, index, middle, ring, pinky]
        
        Returns:
            Processed image with visual feedback
        """
        # Extract landmark positions if hand detected
        if len(lm_list) != 0:
            x1, y1 = lm_list[8][1:]   # Index finger
            x2, y2 = lm_list[12][1:]  # Middle finger
            x3, y3 = lm_list[4][1:]   # Thumb tip
            x5, y5 = lm_list[20][1:]  # Pinky tip
            wrist_y = lm_list[0][2] if len(lm_list) > 0 else y5  # Use wrist for more stable reference
        else:
            # No hand detected, reset drag state
            if self.drag_active:
                self.mouse_controller.toggle_drag(False)
                self.drag_active = False
                self.drag_mode = False
            return img
        
        # Draw frame boundary
        cv2.rectangle(img, (FRAME_REDUCTION, FRAME_REDUCTION), 
                     (CAMERA_WIDTH - FRAME_REDUCTION, CAMERA_HEIGHT - FRAME_REDUCTION),
                     COLOR_FRAME_BOUNDARY, 2)
        
        # Handle scroll mode (priority)
        if fingers[4] == 1 and fingers[3] == 1 and sum(fingers[:3]) == 0:  # Only ring + pinky up
            img = self._handle_scroll(img, wrist_y)
            # Deactivate drag if active during scroll
            if self.drag_active:
                self.mouse_controller.toggle_drag(False)
                self.drag_active = False
                self.drag_mode = False
        else:
            self.scroll_handler.deactivate_scroll_mode()
            
            # Handle movement and drag
            if fingers[1] == 1:  # Index finger up
                img = self._handle_movement(img, x1, y1, fingers)
            else:
                # Reset drag when index finger goes down
                if self.drag_active:
                    self.mouse_controller.toggle_drag(False)
                    self.drag_active = False
                    self.drag_mode = False
            
            # Handle clicks (only if not dragging)
            if not self.drag_active:
                img = self._handle_left_click(img, fingers, lm_list)
                img = self._handle_right_click(img, fingers, lm_list)
        
        return img
    
    def _handle_movement(self, img, x1, y1, fingers):
        """
        Handle mouse movement and drag.
        
        Args:
            img: Current frame
            x1, y1: Index finger coordinates
            fingers: Finger states
        """
        # Map hand coordinates to screen coordinates
        x_mapped = np.interp(x1, (FRAME_REDUCTION, CAMERA_WIDTH - FRAME_REDUCTION), (0, self.w_screen))
        y_mapped = np.interp(y1, (FRAME_REDUCTION, CAMERA_HEIGHT - FRAME_REDUCTION), (0, self.h_screen))
        
        # Apply smoothing
        self.cloc_x = self.ploc_x + (x_mapped - self.ploc_x) / SMOOTHENING
        self.cloc_y = self.ploc_y + (y_mapped - self.ploc_y) / SMOOTHENING
        
        # Move mouse
        self.mouse_controller.move(self.cloc_x, self.cloc_y)
        cv2.circle(img, (x1, y1), 15, COLOR_MOVE_POINTER, cv2.FILLED)
        self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y
        
        # Handle drag: Thumb + Index pinch & hold
        if fingers[0] == 1:  # Thumb up
            length, img, _ = self.detector.find_distance(4, 8, img)
            if length < PINCH_DISTANCE_THRESHOLD:
                if not self.drag_mode:
                    self.drag_start_time = time.time()
                    self.drag_mode = True
                elif (time.time() - self.drag_start_time > DRAG_CLICK_THRESHOLD and 
                      not self.drag_active):
                    self.mouse_controller.toggle_drag(True)
                    self.drag_active = True
                    cv2.putText(img, "DRAGGING", (20, 150), 
                               cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            else:
                # Pinch released
                if self.drag_active:
                    self.mouse_controller.toggle_drag(False)
                    self.drag_active = False
                    self.drag_mode = False
        else:
            # Thumb down - stop drag
            if self.drag_active:
                self.mouse_controller.toggle_drag(False)
                self.drag_active = False
                self.drag_mode = False
        
        return img
    
    def _handle_left_click(self, img, fingers, lm_list):
        """
        Handle left click gesture (index + middle finger).
        
        Args:
            img: Current frame
            fingers: Finger states
            lm_list: Landmark list
        """
        if fingers[1] == 1 and fingers[2] == 1:  # Index and middle up
            length, img, line_info = self.detector.find_distance(8, 12, img)
            if length < PINCH_DISTANCE_THRESHOLD:
                cv2.circle(img, (line_info[4], line_info[5]), 15, COLOR_LEFT_CLICK, cv2.FILLED)
                self.mouse_controller.click()
                time.sleep(0.3)
        return img
    
    def _handle_right_click(self, img, fingers, lm_list):
        """
        Handle right click gesture (thumb + index, middle down).
        
        Args:
            img: Current frame
            fingers: Finger states
            lm_list: Landmark list
        """
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0:  # Thumb + index, middle down
            length, img, line_info = self.detector.find_distance(4, 8, img)
            if length < PINCH_DISTANCE_THRESHOLD:
                cv2.circle(img, (line_info[4], line_info[5]), 15, COLOR_RIGHT_CLICK, cv2.FILLED)
                self.mouse_controller.right_click()
                time.sleep(0.3)
        return img
    
    def _handle_scroll(self, img, wrist_y):
        """
        Handle scroll gesture (ring + pinky up).
        
        Args:
            img: Current frame
            wrist_y: Y coordinate of wrist
        """
        # Activate scroll mode if not already active
        if not self.scroll_handler.is_scroll_mode_active():
            self.scroll_handler.activate_scroll_mode()
            cv2.putText(img, "SCROLL MODE", (20, 150),
                       cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 0), 3)
        
        # Calculate progressive scroll speed
        scroll_speed = self.scroll_handler.get_progressive_speed(wrist_y)
        
        # Visual feedback for scroll zones
        neutral_top, neutral_bottom, _ = self.scroll_handler.get_scroll_zones()
        
        # Draw neutral zone
        cv2.rectangle(img, (0, neutral_top), (CAMERA_WIDTH, neutral_bottom), 
                     (0, 255, 0), 1)
        # Draw acceleration zones
        cv2.rectangle(img, (0, 0), (CAMERA_WIDTH, neutral_top), (0, 0, 255), 1)  # Top zone
        cv2.rectangle(img, (0, neutral_bottom), (CAMERA_WIDTH, CAMERA_HEIGHT), (0, 0, 255), 1)  # Bottom zone
        
        # Perform scroll if conditions are met
        if self.scroll_handler.should_scroll(scroll_speed):
            # Apply smoothing
            smoothed_scroll = self.scroll_handler.smooth_scroll(scroll_speed)
            
            # Perform the scroll with boost
            self.mouse_controller.scroll(int(smoothed_scroll * SCROLL_BOOST_MULTIPLIER))
            
            # Show current scroll speed
            speed_text = f"SPEED: {abs(int(smoothed_scroll)):02d}"
            cv2.putText(img, speed_text, (CAMERA_WIDTH - 200, 50),
                       cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
            
            # Show hand position indicator
            pos_text = f"POS: {wrist_y}"
            cv2.putText(img, pos_text, (CAMERA_WIDTH - 200, 80),
                       cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)
            
            self.scroll_handler.update_scroll_time()
        
        return img
    
    def cleanup(self):
        """Clean up resources, ensure drag is released."""
        if self.drag_active:
            self.mouse_controller.toggle_drag(False)

