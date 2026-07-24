# src/monitoring/activity_detector.py
"""Activity detection and pattern recognition"""

import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ActivityDetector:
    """Detect and classify user activity patterns"""
    
    def __init__(self):
        self.activity_history = []
        self.current_activity = None
        self.activity_threshold = 5  # seconds
        self.last_activity_time = time.time()
        self.idle_time = 0
        
    def update_activity(self, activity_type: str, details: Optional[Dict] = None):
        """Update current activity"""
        current_time = time.time()
        
        # Check if activity has changed
        if self.current_activity and self.current_activity['type'] != activity_type:
            # End previous activity
            self.current_activity['end_time'] = datetime.now().isoformat()
            self.activity_history.append(self.current_activity)
            
            # Start new activity
            self.current_activity = {
                'type': activity_type,
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'details': details or {}
            }
        elif not self.current_activity:
            # First activity
            self.current_activity = {
                'type': activity_type,
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'details': details or {}
            }
        else:
            # Update details of current activity
            if details:
                self.current_activity['details'].update(details)
        
        self.last_activity_time = current_time
        self.idle_time = 0
    
    def update_idle_time(self):
        """Update idle time when no activity detected"""
        self.idle_time = time.time() - self.last_activity_time
    
    def is_idle(self, threshold: int = 10) -> bool:
        """Check if user is idle"""
        return self.idle_time > threshold
    
    def get_current_activity(self) -> Optional[Dict[str, Any]]:
        """Get current activity"""
        if self.current_activity:
            # Update duration
            if self.current_activity['end_time'] is None:
                start = datetime.fromisoformat(self.current_activity['start_time'])
                duration = (datetime.now() - start).total_seconds()
                return {
                    **self.current_activity,
                    'duration': duration,
                    'idle_time': self.idle_time
                }
        return None
    
    def get_activity_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get activity history"""
        return self.activity_history[-limit:]
    
    def clear_history(self):
        """Clear activity history"""
        self.activity_history = []
        self.current_activity = None