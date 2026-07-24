# src/alert/alert_system.py
"""Alert system with continuous sound - Fixed"""

import time
import threading
from typing import Optional, Dict, Any, Callable
from datetime import datetime
import logging
from pathlib import Path

from .sound_manager import SoundManager
from .task_generator import TaskGenerator
from .notification import NotificationManager

logger = logging.getLogger(__name__)

class AlertSystem:
    """Manage alerts, sounds, and wake-up tasks"""
    
    def __init__(self):
        self.sound_manager = SoundManager()
        self.task_generator = TaskGenerator()
        self.notification_manager = NotificationManager()
        
        self.active_task = None
        self.task_completed = False
        self.task_start_time = None
        self.task_timeout = 30
        self.alert_history = []
        self.alert_callbacks = []
        
        # Continuous sound management
        self.sound_thread = None
        self.sound_stop_event = threading.Event()
        self.is_sound_playing = False
        self.current_alert_type = None
        self.sound_lock = threading.Lock()
        
        # Alert cooldown
        self.last_alert_time = 0
        self.alert_cooldown = 3
    
    def trigger_alert(self, alert_type: str, message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """Trigger an alert"""
        current_time = time.time()
        
        # Check cooldown for distraction alerts
        if alert_type == "distraction" and current_time - self.last_alert_time < self.alert_cooldown:
            return {"status": "cooldown", "message": "Alert cooldown active"}
        
        self.last_alert_time = current_time
        
        # Log alert
        alert_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "message": message,
            "details": details or {}
        }
        self.alert_history.append(alert_entry)
        
        # Handle different alert types
        if alert_type == "distraction":
            # Start continuous sound
            self.start_continuous_sound("distraction")
            self.current_alert_type = "distraction"
            
            # Show notification (will show overlay)
            self.notification_manager.show_notification(
                title="⚠️ FOCUS ALERT!",
                message=message,
                notification_type="warning"
            )
            
        elif alert_type == "focus_restored":
            # Stop continuous sound
            self.stop_continuous_sound()
            self.current_alert_type = None
            
            # Close any open popups
            self.notification_manager.close_all_popups()
            
            # Show notification
            self.notification_manager.show_notification(
                title="✅ Focus Restored!",
                message=message,
                notification_type="info"
            )
            
        elif alert_type == "sleepiness":
            # Play wake-up sound
            self.sound_manager.play_alert_sound("wake_up")
            self.current_alert_type = "sleepiness"
            
            # Show notification
            self.notification_manager.show_notification(
                title="😴 Wake Up!",
                message=message,
                notification_type="warning"
            )
            
            # Generate task
            task = self.generate_task()
            return {
                "status": "success",
                "type": alert_type,
                "message": message,
                "task": task
            }
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, message, details)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        return {"status": "success", "type": alert_type, "message": message}
    
    def start_continuous_sound(self, sound_type: str = "distraction"):
        """Start playing continuous sound in background"""
        with self.sound_lock:
            if self.is_sound_playing:
                return
            
            self.is_sound_playing = True
            self.sound_stop_event.clear()
            
            def play_loop():
                """Play sound in loop until stopped"""
                sound_file = Path("C:/Users/bhanu/Desktop/New folder/sound.mp3")
                
                while not self.sound_stop_event.is_set():
                    try:
                        if sound_file.exists():
                            self.sound_manager.play_custom_sound(str(sound_file))
                        else:
                            self.sound_manager.play_alert_sound("alert")
                        
                        # Wait a bit between plays
                        for _ in range(5):
                            if self.sound_stop_event.is_set():
                                break
                            time.sleep(0.2)
                            
                    except Exception as e:
                        logger.error(f"Error in sound loop: {e}")
                        time.sleep(0.5)
                
                self.is_sound_playing = False
            
            self.sound_thread = threading.Thread(target=play_loop)
            self.sound_thread.daemon = True
            self.sound_thread.start()
            logger.info(f"Continuous sound started for {sound_type}")
    
    def stop_continuous_sound(self):
        """Stop the continuous sound"""
        with self.sound_lock:
            if not self.is_sound_playing:
                return

            self.sound_stop_event.set()
            sound_thread = self.sound_thread

        # Do not wait while holding sound_lock. The worker may still be
        # finishing an audio call and must be able to leave the loop cleanly.
        if sound_thread and sound_thread is not threading.current_thread():
            sound_thread.join(timeout=1)

        with self.sound_lock:
            self.is_sound_playing = False
            if self.sound_thread is sound_thread:
                self.sound_thread = None
        logger.info("Continuous sound stopped")
    
    def generate_task(self) -> Dict[str, Any]:
        """Generate a wake-up task"""
        task = self.task_generator.generate_task()
        self.active_task = task
        self.task_completed = False
        self.task_start_time = time.time()
        
        return {
            "task": task,
            "timeout": self.task_timeout,
            "start_time": self.task_start_time
        }
    
    def verify_task(self, user_input: str) -> Dict[str, Any]:
        """Verify task completion"""
        if not self.active_task:
            return {"status": "error", "message": "No active task"}
        
        # Check timeout
        if time.time() - self.task_start_time > self.task_timeout:
            self.task_completed = False
            self.active_task = None
            return {"status": "timeout", "message": "Task timed out"}
        
        # Verify task
        result = self.task_generator.verify_task(self.active_task, user_input)
        
        if result["status"] == "success":
            self.task_completed = True
            self.active_task = None
            self.sound_manager.play_alert_sound("success")
            self.stop_continuous_sound()
            self.notification_manager.close_all_popups()
        
        return result
    
    def get_active_task(self) -> Optional[Dict[str, Any]]:
        """Get current active task"""
        if self.active_task and not self.task_completed:
            elapsed = time.time() - self.task_start_time
            remaining = max(0, self.task_timeout - elapsed)
            return {
                "task": self.active_task,
                "remaining_time": remaining,
                "completed": False
            }
        return None
    
    def add_callback(self, callback: Callable):
        """Add callback for alerts"""
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def get_alert_history(self, limit: int = 10) -> list:
        """Get alert history"""
        return self.alert_history[-limit:]
    
    def clear_history(self):
        """Clear alert history"""
        self.alert_history = []
    
    def stop(self):
        """Stop all alert system activities"""
        self.stop_continuous_sound()
        self.notification_manager.close_all_popups()
        self.notification_manager.stop()