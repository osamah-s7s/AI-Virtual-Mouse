"""
Virtual Mouse - Hand Gesture Controlled Mouse
Main entry point for the application.

Controls your computer mouse using hand gestures detected via webcam.
"""

import cv2
from src.camera import initialize_camera
from src.hand_detector import HandDetector
from src.mouse_controller import MouseController
from src.gesture_handler import GestureHandler
from src.utils import FPSCounter
from src.config import WINDOW_TITLE


def main():
    """
    Main application loop.
    Initializes all components and runs the gesture recognition loop.
    """
    # Initialize camera
    print("Initializing camera...")
    cap = initialize_camera()
    
    # Initialize components
    detector = HandDetector(max_hands=1)
    mouse_controller = MouseController()
    gesture_handler = GestureHandler(detector, mouse_controller)
    fps_counter = FPSCounter()
    
    print("Virtual Mouse started. Press 'q' to quit.")
    print("\nGestures:")
    print("- Point with index finger: Move mouse")
    print("- Index + Middle finger pinch: Left click")
    print("- Thumb + Index finger pinch: Right click")
    print("- Thumb + Index pinch & hold: Drag")
    print("- Ring + Pinky up: Scroll mode")
    print()
    
    try:
        # Main loop
        while True:
            success, img = cap.read()
            if not success:
                print("Failed to read from camera")
                continue
            
            # Detect hands and landmarks
            img = detector.find_hands(img)
            lm_list, bbox = detector.find_position(img, draw=False)
            
            # Get finger states
            fingers = detector.fingers_up() if len(lm_list) != 0 else [0, 0, 0, 0, 0]
            
            # Process gestures
            img = gesture_handler.process_frame(img, lm_list, fingers)
            
            # Update and display FPS
            fps = fps_counter.update()
            img = fps_counter.draw_fps(img, fps)
            
            # Display frame
            cv2.imshow(WINDOW_TITLE, img)
            
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Cleanup
        print("Cleaning up...")
        gesture_handler.cleanup()
        cap.release()
        cv2.destroyAllWindows()
        print("Application closed.")


if __name__ == "__main__":
    main()

