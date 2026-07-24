# src/monitoring/webcam_monitor.py
"""Webcam monitoring with face and eye detection"""

import cv2
import numpy as np
import time
import threading
from collections import deque
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    import mediapipe as mp
except ImportError:
    mp = None
    logger.warning("MediaPipe is not installed; webcam monitoring is unavailable")

class WebcamMonitor:
    """Monitor user through webcam"""
    
    def __init__(self):
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.is_available = mp is not None
        self.monitoring_thread: Optional[threading.Thread] = None
        
        # Face detection
        if self.is_available:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5
            )

            # Face mesh for eye detection
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        else:
            self.face_detection = None
            self.face_mesh = None
        
        # Eye landmarks
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # State variables
        self.face_detected = False
        self.face_timer = 0
        self.last_face_time = time.time()
        self.absence_alerted = False
        self.eye_aspect_ratios = deque(maxlen=10)
        self.sleepiness_level = 0
        self.eyes_closed_count = 0
        self.eyes_closed_threshold = 30  # frames
        
        # Callbacks
        self.alert_callbacks: list = []
        
        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()
    
    def start_monitoring(self, camera_id: int = 0) -> Dict[str, Any]:
        """Start webcam monitoring"""
        if not self.is_available:
            return {"status": "error", "message": "MediaPipe is not installed; webcam monitoring is unavailable"}

        if self.is_running:
            return {"status": "error", "message": "Monitoring already running"}
        
        try:
            self.cap = cv2.VideoCapture(camera_id)
            if not self.cap.isOpened():
                return {"status": "error", "message": "Could not open webcam"}
            
            self.is_running = True
            self.last_face_time = time.time()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(target=self._monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            logger.info("Webcam monitoring started")
            return {"status": "success", "message": "Webcam monitoring started"}
            
        except Exception as e:
            logger.error(f"Error starting webcam: {e}")
            return {"status": "error", "message": str(e)}
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running and self.cap:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                # Process frame
                self._process_frame(frame)
                
                # Check for alerts
                self._check_alert_conditions()
                
                # Update FPS
                self.frame_count += 1
                if time.time() - self.last_fps_time >= 1.0:
                    self.fps = self.frame_count
                    self.frame_count = 0
                    self.last_fps_time = time.time()
                
                # Control frame rate (reduce CPU usage)
                time.sleep(0.03)  # ~30 FPS
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, frame: np.ndarray):
        """Process a single frame"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Face detection
        face_results = self.face_detection.process(rgb_frame)
        if face_results.detections:
            self.face_detected = True
            self.last_face_time = time.time()
            self.face_timer = 0
            self.absence_alerted = False
            
            # Process for eye detection
            self._process_eyes(rgb_frame)
        else:
            self.face_detected = False
            self.face_timer += 1 / 30  # approximate seconds
    
    def _process_eyes(self, frame: np.ndarray):
        """Process eye detection for sleepiness"""
        try:
            face_results = self.face_mesh.process(frame)
            
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    # Calculate eye aspect ratio
                    ear = self._calculate_ear(face_landmarks.landmark)
                    self.eye_aspect_ratios.append(ear)
                    
                    # Check if eyes are closed
                    if ear < 0.2:  # Threshold for closed eyes
                        self.eyes_closed_count += 1
                    else:
                        self.eyes_closed_count = max(0, self.eyes_closed_count - 1)
                    
                    # If eyes closed for more than threshold
                    if self.eyes_closed_count > self.eyes_closed_threshold:
                        self.sleepiness_level += 1
                        if self.sleepiness_level > 10:
                            self._trigger_alert("sleepiness", "User appears to be sleeping!")
                            self.sleepiness_level = 0
                    else:
                        self.sleepiness_level = max(0, self.sleepiness_level - 0.5)
                        
        except Exception as e:
            logger.error(f"Error in eye processing: {e}")
    
    def _calculate_ear(self, landmarks) -> float:
        """Calculate Eye Aspect Ratio"""
        try:
            # Get eye landmarks
            left_eye_points = [landmarks[i] for i in self.LEFT_EYE]
            right_eye_points = [landmarks[i] for i in self.RIGHT_EYE]
            
            # Calculate EAR for both eyes
            left_ear = self._eye_aspect_ratio(left_eye_points)
            right_ear = self._eye_aspect_ratio(right_eye_points)
            
            return (left_ear + right_ear) / 2.0
        except:
            return 1.0
    
    def _eye_aspect_ratio(self, eye_points) -> float:
        """Calculate Eye Aspect Ratio for given points"""
        try:
            # Vertical distances
            v1 = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
            v2 = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
            
            # Horizontal distance
            h = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
            
            if h == 0:
                return 1.0
            
            ear = (v1 + v2) / (2.0 * h)
            return ear
        except:
            return 1.0
    
    def _check_alert_conditions(self):
        """Check various conditions and trigger alerts"""
        # Check if user has been absent for too long
        if time.time() - self.last_face_time > 30 and not self.absence_alerted:  # 30 seconds
            self.absence_alerted = True
            self._trigger_alert("absence", "User not in front of screen!")
    
    def _trigger_alert(self, alert_type: str, message: str):
        """Trigger alert for various conditions"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, message, datetime.now())
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alerts"""
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop webcam monitoring"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
            self.monitoring_thread = None
        
        logger.info("Webcam monitoring stopped")
        return {"status": "success", "message": "Webcam monitoring stopped"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "is_running": self.is_running,
            "is_available": self.is_available,
            "face_detected": self.face_detected,
            "face_absent_seconds": time.time() - self.last_face_time if not self.face_detected else 0,
            "absence_alerted": self.absence_alerted,
            "sleepiness_level": self.sleepiness_level,
            "fps": self.fps
        }
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame for display"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None