"""
Camera initialization utilities.
Handles camera detection and setup with multiple backend support.
"""

import cv2
from .config import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_PRIORITIES


def initialize_camera():
    """
    Initialize camera with automatic detection.
    Tries DirectShow backend first (Windows), then falls back to default backend.
    
    Returns:
        cv2.VideoCapture: Initialized camera object, or None if no camera found
    
    Raises:
        SystemExit: If no camera could be initialized
    """
    cap = None
    
    # Try DirectShow backend first (Windows-specific)
    for camera_idx in CAMERA_PRIORITIES:
        cap = cv2.VideoCapture(camera_idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, test_frame = cap.read()
            if ret:
                print(f"Camera found at index {camera_idx}")
                break
            else:
                cap.release()
                cap = None
        else:
            if cap:
                cap.release()
            cap = None
    
    # If DirectShow didn't work, try default backend
    if cap is None or not cap.isOpened():
        for camera_idx in CAMERA_PRIORITIES[:3]:  # Try first 3 indices
            cap = cv2.VideoCapture(camera_idx)
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret:
                    print(f"Camera found at index {camera_idx} (default backend)")
                    break
                else:
                    cap.release()
                    cap = None
            else:
                if cap:
                    cap.release()
                cap = None
    
    if cap is None or not cap.isOpened():
        print("ERROR: Could not open any camera. Please check:")
        print("1. Camera is connected and not in use by another application")
        print("2. Camera permissions are granted")
        print("3. Try restarting the application")
        raise SystemExit(1)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    return cap

