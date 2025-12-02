"""
Hand Detection Module using MediaPipe.
Provides HandDetector class for detecting and tracking hand landmarks.
"""

import cv2
import mediapipe as mp
import math


class HandDetector:
    """
    Hand detector using MediaPipe for hand tracking.
    Detects hand landmarks and provides utilities for gesture recognition.
    """
    
    def __init__(self, mode=False, max_hands=2, detection_con=0.5, track_con=0.5):
        """
        Initialize the HandDetector.
        
        Args:
            mode: If True, treats input images as static images
            max_hands: Maximum number of hands to detect
            detection_con: Minimum detection confidence threshold
            track_con: Minimum tracking confidence threshold
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]  # Landmark IDs for finger tips

    def find_hands(self, img, draw=True):
        """
        Detect hands in the image and optionally draw landmarks.
        
        Args:
            img: Input image (BGR format)
            draw: If True, draw hand landmarks and connections
        
        Returns:
            Image with or without drawn landmarks
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Get hand landmark positions in pixel coordinates.
        
        Args:
            img: Input image
            hand_no: Which hand to track (0 for first detected hand)
            draw: If True, draw landmarks and bounding box
        
        Returns:
            tuple: (landmark_list, bbox)
                - landmark_list: List of [id, x, y] for each landmark
                - bbox: Bounding box as (x_min, y_min, x_max, y_max)
        """
        x_list = []
        y_list = []
        bbox = []
        self.lm_list = []
        
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                x_list.append(cx)
                y_list.append(cy)
                self.lm_list.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            bbox = x_min, y_min, x_max, y_max

            if draw:
                cv2.rectangle(img, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20),
                              (0, 255, 0), 2)

        return self.lm_list, bbox

    def fingers_up(self):
        """
        Determine which fingers are up.
        
        Returns:
            List of 5 integers [thumb, index, middle, ring, pinky]
            where 1 means finger is up, 0 means down
        """
        fingers = []
        # Safety check - return all fingers down if no landmarks
        if not hasattr(self, 'lm_list') or len(self.lm_list) < 21:  # 21 landmarks in mediapipe hand model
            return [0, 0, 0, 0, 0]
        
        # Thumb (more robust check)
        try:
            thumb_up = self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]
            fingers.append(1 if thumb_up else 0)
        except (IndexError, TypeError):
            fingers.append(0)

        # Other fingers
        for id in range(1, 5):
            try:
                finger_up = self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]
                fingers.append(1 if finger_up else 0)
            except (IndexError, TypeError):
                fingers.append(0)
        
        return fingers

    def find_distance(self, p1, p2, img, draw=True, r=15, t=3):
        """
        Calculate distance between two landmark points.
        
        Args:
            p1: First landmark ID
            p2: Second landmark ID
            img: Image to draw on
            draw: If True, draw line and circles
            r: Circle radius
            t: Line thickness
        
        Returns:
            tuple: (length, img, [x1, y1, x2, y2, cx, cy])
        """
        if not hasattr(self, 'lm_list') or len(self.lm_list) < max(p1, p2) + 1:
            return 0, img, [0, 0, 0, 0, 0, 0]
            
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
            
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

