"""
Configuration constants for the Virtual Mouse application.
All settings and parameters are centralized here.
"""

# Camera settings
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_PRIORITIES = [2, 0, 1, 3, 4]  # Prioritize camera index 2

# Frame settings
FRAME_REDUCTION = 100  # Frame Reduction area
SMOOTHENING = 7  # Mouse movement smoothing factor

# Scroll configuration
BASE_SCROLL_SENSITIVITY = 5.0  # Base scroll speed
MAX_SCROLL_SENSITIVITY = 20.0  # Maximum scroll speed at edges
SCROLL_DELAY = 0.02  # Delay between scroll actions (seconds)
SCROLL_HISTORY_LENGTH = 3  # Number of scroll values to average for smoothing

# Drag configuration
DRAG_CLICK_THRESHOLD = 0.3  # Time to hold pinch before drag activates (seconds)

# Gesture thresholds
PINCH_DISTANCE_THRESHOLD = 40  # Distance threshold for pinch gestures (pixels)

# Display settings
WINDOW_TITLE = "Osamah H. Alaini"
FPS_DISPLAY_POSITION = (20, 50)
FPS_FONT_SCALE = 3
FPS_COLOR = (255, 0, 0)
FPS_THICKNESS = 3

# Visual feedback colors (BGR format)
COLOR_MOVE_POINTER = (255, 0, 255)  # Magenta
COLOR_LEFT_CLICK = (0, 255, 0)  # Green
COLOR_RIGHT_CLICK = (0, 255, 255)  # Yellow
COLOR_FRAME_BOUNDARY = (255, 0, 255)  # Magenta
COLOR_SCROLL_NEUTRAL_ZONE = (0, 255, 0)  # Green
COLOR_SCROLL_ACCELERATION_ZONE = (0, 0, 255)  # Red

# Scroll zone visualization
SCROLL_NEUTRAL_ZONE_HEIGHT_RATIO = 1/5  # Neutral zone is 1/5 of camera height
SCROLL_BOOST_MULTIPLIER = 15  # Multiplier for scroll speed

