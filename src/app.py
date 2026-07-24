# src/app.py
"""Main application orchestrator - Fixed for no auto-close"""

import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from core.focus_mode import FocusMode
from core.session_manager import SessionManager
from core.config import ConfigManager
from monitoring.webcam_monitor import WebcamMonitor
from monitoring.screen_monitor import ScreenMonitor
from monitoring.media_controllers import MediaController
from alert.alert_system import AlertSystem

logger = logging.getLogger(__name__)

class FocusApplication:
    """Main application orchestrator"""
    
    def __init__(self):
        # Initialize components
        self.focus_mode = FocusMode()
        self.session_manager = SessionManager()
        self.config = ConfigManager()
        self.webcam_monitor = WebcamMonitor()
        self.screen_monitor = ScreenMonitor()
        self.media_controller = MediaController()
        self.alert_system = AlertSystem()
        
        # State
        self.is_active = False
        self.user_present = True
        self.sleep_alert_triggered = False
        self.current_session_id = None
        self.distraction_active = False
        self.should_keep_running = True  # Added to prevent auto-close
        
        # Register callbacks
        self._register_callbacks()
        
        logger.info("Focus Application initialized")
    
    def _register_callbacks(self):
        """Register callbacks between components"""
        # Focus mode callbacks
        self.focus_mode.register_callback('state_change', self._on_focus_state_change)
        self.focus_mode.register_callback('time_update', self._on_time_update)
        self.focus_mode.register_callback('interruption', self._on_interruption)
        self.focus_mode.register_callback('completion', self._on_completion)
        
        # Webcam callbacks
        self.webcam_monitor.add_alert_callback(self._on_webcam_alert)
        
        # Screen callbacks
        self.screen_monitor.add_alert_callback(self._on_screen_alert)
    
    def _on_focus_state_change(self, event_type: str, data: Dict[str, Any]):
        """Handle focus state changes"""
        state = data.get('state')
        logger.info(f"Focus state changed: {state}")
        
        if state in ['completed', 'interrupted']:
            self._stop_all_monitoring()
            self.is_active = False
            
            # Save session
            if self.current_session_id:
                session_data = data.get('session', {})
                if session_data:
                    self.session_manager.save_session(session_data)
                    self.session_manager.update_stats()
            
            # Stop sounds but keep app running
            self.alert_system.stop_continuous_sound()
            self.alert_system.notification_manager.close_all_popups()
            logger.info("Session ended, app still running")
    
    def _on_time_update(self, event_type: str, data: Dict[str, Any]):
        """Handle time updates"""
        # Could update UI here
        pass
    
    def _on_interruption(self, event_type: str, data: Dict[str, Any]):
        """Handle interruptions"""
        reason = data.get('reason', 'Unknown')
        self.alert_system.trigger_alert(
            "interruption",
            f"Focus interrupted: {reason}",
            {"reason": reason}
        )
    
    def _on_completion(self, event_type: str, data: Dict[str, Any]):
        """Handle session completion"""
        self.alert_system.trigger_alert(
            "timer_end",
            "🎉 Focus session completed! Great job!",
            data
        )
        # Stop sounds but keep app running
        self.alert_system.stop_continuous_sound()
        self.alert_system.notification_manager.close_all_popups()
        logger.info("Session completed, app still running")
    
    def _on_webcam_alert(self, alert_type: str, message: str, timestamp: datetime):
        """Handle webcam alerts"""
        logger.info(f"Webcam alert: {alert_type} - {message}")
        
        if alert_type == "sleepiness":
            self.sleep_alert_triggered = True
            result = self.alert_system.trigger_alert(
                "sleepiness",
                "😴 You look sleepy! Wake up and complete the task!",
                {"type": "sleep_detected"}
            )
            if result.get('task'):
                logger.info(f"Wake-up task generated: {result['task']}")
                
        elif alert_type == "absence":
            self.user_present = False
            result = self.handle_user_absence()
            if result.get("status") == "paused":
                logger.info("YouTube paused - user away from screen")
    
    def _on_screen_alert(self, alert_type: str, message: str, details: Dict):
        """Handle screen alerts"""
        logger.info(f"Screen alert: {alert_type} - {message}")
        
        if alert_type == "distraction":
            self.distraction_active = True
            self.alert_system.trigger_alert(
                "distraction",
                f"⚠️ FOCUS ALERT: {message}",
                details
            )

            # Keep the session and screen monitor running so closing the
            # distracting window can be detected and the alert can stop.
            logger.info("Distraction detected; focus timer remains running")
                
        elif alert_type == "focus_restored":
            self.distraction_active = False
            self.alert_system.trigger_alert(
                "focus_restored",
                "✅ Focus restored! Keep going! 💪",
                details
            )
            # Stop sound but keep app running
            self.alert_system.stop_continuous_sound()
            self.alert_system.notification_manager.close_all_popups()
            logger.info("Focus restored - sound stopped, app still running")
    
    def start_focus_session(self, duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Start a new focus session"""
        if self.is_active:
            return {"status": "error", "message": "Focus session already active"}
        
        if duration_minutes is None:
            duration_minutes = self.config.get('default_focus_duration', 25)
        
        result = self.focus_mode.start_session(duration_minutes)
        if result['status'] != 'success':
            return result
        
        if self.config.get('webcam_enabled', True):
            self.webcam_monitor.start_monitoring()
        
        if self.config.get('screen_monitoring_enabled', True):
            self.screen_monitor.start_monitoring()
        
        self.is_active = True
        self.current_session_id = result.get('session_id')
        self.user_present = True
        self.sleep_alert_triggered = False
        self.distraction_active = False
        
        logger.info(f"Focus session started: {self.current_session_id}")
        return result
    
    def pause_focus_session(self) -> Dict[str, Any]:
        """Pause the current session"""
        result = self.focus_mode.pause_session()
        if result['status'] == 'success':
            logger.info("Focus session paused")
            self.alert_system.stop_continuous_sound()
        return result
    
    def resume_focus_session(self) -> Dict[str, Any]:
        """Resume the current session"""
        result = self.focus_mode.resume_session()
        if result['status'] == 'success':
            logger.info("Focus session resumed")
        return result
    
    def stop_focus_session(self) -> Dict[str, Any]:
        """Stop the current session"""
        if not self.is_active:
            return {"status": "error", "message": "No active session"}
        
        # Stop monitoring and sounds but keep app running
        self._stop_all_monitoring()
        self.alert_system.stop_continuous_sound()
        self.alert_system.notification_manager.close_all_popups()
        
        result = self.focus_mode.interrupt_session("User stopped session")
        self.is_active = False
        logger.info("Session stopped, app still running")
        return result
    
    def _stop_all_monitoring(self):
        """Stop all monitoring"""
        self.webcam_monitor.stop_monitoring()
        self.screen_monitor.stop_monitoring()
        # Don't set is_active to False here - let the caller handle it
    
    def handle_user_absence(self) -> Dict[str, Any]:
        """Handle when user is absent"""
        if self.user_present or not self.config.get('auto_pause_youtube', True):
            return {"status": "no_action"}

        # Never send media keys blindly: the active window must be YouTube.
        if self.media_controller.detect_youtube_tab():
            result = self.media_controller.pause_youtube()
            if result.get("status") == "success":
                return {"status": "paused", "platform": "YouTube"}
        return {"status": "no_action"}
    
    def verify_task(self, user_input: str) -> Dict[str, Any]:
        """Verify wake-up task"""
        result = self.alert_system.verify_task(user_input)
        
        if result["status"] == "success":
            self.sleep_alert_triggered = False
            self.user_present = True
            
            if self.media_controller.is_paused:
                self.media_controller.resume_youtube()
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get current application status"""
        return {
            "is_active": self.is_active,
            "user_present": self.user_present,
            "distraction_active": self.distraction_active,
            "focus_status": self.focus_mode.get_status(),
            "webcam_status": self.webcam_monitor.get_status(),
            "screen_status": self.screen_monitor.get_status(),
            "youtube_status": self.media_controller.get_status(),
            "alert_status": {
                "sleep_alert_triggered": self.sleep_alert_triggered,
                "active_task": self.alert_system.get_active_task(),
                "recent_alerts": self.alert_system.get_alert_history(5),
                "is_sound_playing": self.alert_system.is_sound_playing
            }
        }
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics"""
        return self.session_manager.get_stats(days)
    
    def cleanup(self):
        """Clean up all resources - called when app is closing"""
        logger.info("Cleaning up application resources...")
        self.alert_system.stop()
        self._stop_all_monitoring()
        self.alert_system.stop_continuous_sound()
        self.alert_system.notification_manager.close_all_popups()
        self.should_keep_running = False
        logger.info("Cleanup complete")