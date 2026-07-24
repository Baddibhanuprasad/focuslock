# src/monitoring/screen_monitor.py
"""Screen and application monitoring with better distraction detection"""

import psutil
import time
import threading
import re
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    import pygetwindow as gw
except ImportError:
    gw = None
    logger.warning("pygetwindow is not installed; screen monitoring is unavailable")

class ScreenMonitor:
    """Monitor screen for entertainment content"""
    
    def __init__(self):
        self.is_running = False
        self.is_available = gw is not None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.alert_callbacks: list = []
        
        # Entertainment patterns - more specific for better detection
        self.distraction_patterns = {
            'youtube_shorts': ['youtube.com/shorts', 'youtu.be/shorts', 'shorts', 'Short', '/shorts/', 'shorts/'],
            'youtube_music': ['music.youtube.com', 'youtube.com/music', 'youtu.be/music', 'YouTube Music', 'music.youtube'],
            'instagram': ['instagram.com', 'Instagram', 'reels', '/reel/', 'insta'],
            'netflix': ['netflix.com', 'Netflix'],
            'prime_video': ['primevideo.com', 'Amazon Video'],
            'spotify': ['spotify.com', 'Spotify'],
            'social': ['facebook.com', 'twitter.com', 'tiktok.com', 'reddit.com', 'social'],
            'gaming': ['steam', 'epic games', 'origin', 'play'],
            'music': ['music', 'song', 'audio', 'pandora', 'soundcloud']
        }
        
        # Educational keywords - if these are in the title, allow it
        self.educational_keywords = [
            'tutorial', 'course', 'lecture', 'lesson', 'learn', 'education', 
            'programming', 'python', 'java', 'javascript', 'react', 'angular',
            'math', 'science', 'history', 'english', 'grammar', 'coding',
            'algorithm', 'data structure', 'machine learning', 'AI', 'artificial',
            'neural network', 'deep learning', 'computer science', 'physics',
            'chemistry', 'biology', 'medicine', 'finance', 'economics',
            'photography', 'design', 'photoshop', 'illustrator', 'blender',
            'excel', 'powerpoint', 'word', 'office', 'business', 'marketing',
            'how to', 'guide', 'explained', 'for beginners', 'advanced'
        ]
        
        # YouTube allowed channels (educational)
        self.educational_channels = [
            'khan academy', 'coursera', 'udemy', 'edx', 'mit', 'stanford',
            'harvard', 'youtube learning', 'tedx', 'ted talks', 'crash course',
            'freecodecamp', 'codecademy', 'w3schools', 'geeksforgeeks',
            'programming with mosh', 'traversy media', 'web dev simplified',
            'academind', 'net ninja', 'codevolution', 'fireship',
            'tech with tim', 'sentdex', 'corey schafer', 'derek banas',
            'the new boston', 'kavin kumar', 'hitesh choudhary'
        ]
        
        # State
        self.current_activity = None
        self.distraction_detected = False
        self.distraction_start_time = None
        self.distraction_type = None
        self.is_youtube = False
        self.is_youtube_shorts = False
        self.is_youtube_music = False
        self.is_educational = False
        self.alert_threshold = 2  # seconds before alerting
        self.last_alert_time = 0
        self.alert_cooldown = 8  # seconds between alerts
        self.previous_window_title = ""
        self.window_closed_time = None
        self.window_was_closed = False
        self.last_window_title = ""
        
    def start_monitoring(self) -> Dict[str, Any]:
        """Start screen monitoring"""
        if not self.is_available:
            return {"status": "error", "message": "pygetwindow is not installed; screen monitoring is unavailable"}

        if self.is_running:
            return {"status": "error", "message": "Monitoring already running"}
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        logger.info("Screen monitoring started")
        return {"status": "success", "message": "Screen monitoring started"}
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        window_check_counter = 0
        while self.is_running:
            try:
                self._check_active_window()
                
                # Check for window closed state more frequently
                window_check_counter += 1
                if window_check_counter >= 4:  # Every 2 seconds
                    self._check_window_closed()
                    window_check_counter = 0
                    
                time.sleep(0.5)  # Check every 0.5 seconds
            except Exception as e:
                logger.error(f"Screen monitoring error: {e}")
                time.sleep(1)
    
    def _check_window_closed(self):
        """Check if the window was closed"""
        try:
            active_windows = gw.getAllWindows()
            
            # If no windows are open at all
            if not active_windows:
                if self.distraction_detected:
                    logger.info("All windows closed - resetting distraction state")
                    self._reset_distraction_state()
                    self._trigger_alert("focus_restored", "✅ Focus restored! All windows closed.", {})
                return
            
            # Check if our YouTube window still exists
            if self.is_youtube:
                youtube_window_found = False
                for window in active_windows:
                    if window.title and ('youtube' in window.title.lower() or 'youtu.be' in window.title.lower()):
                        youtube_window_found = True
                        break
                
                if not youtube_window_found and self.distraction_detected:
                    logger.info("YouTube window closed - resetting distraction state")
                    self._reset_distraction_state()
                    self._trigger_alert("focus_restored", "✅ Focus restored! YouTube closed.", {})
                    
        except Exception as e:
            logger.error(f"Error checking window closed: {e}")
    
    def _check_active_window(self):
        """Check active window for distractions"""
        try:
            active_window = gw.getActiveWindow()
            
            # If no active window, check if we have a distraction
            if not active_window:
                if self.distraction_detected:
                    # Wait a bit before resetting (in case it's a quick switch)
                    if self.window_closed_time is None:
                        self.window_closed_time = time.time()
                    elif time.time() - self.window_closed_time > 1.0:
                        logger.info("No active window - resetting distraction state")
                        self._reset_distraction_state()
                        self._trigger_alert("focus_restored", "✅ Focus restored!", {})
                return
            
            # Reset window closed timer
            self.window_closed_time = None
            
            window_title = active_window.title
            process_name = self._get_active_process_name()
            
            # Check if window title changed
            if self.last_window_title != window_title:
                logger.debug(f"Window changed: {window_title}")
                self.last_window_title = window_title
            
            # Check if it's YouTube
            self.is_youtube = self._is_youtube(window_title, process_name)
            self.is_youtube_shorts = self._is_youtube_shorts(window_title)
            self.is_youtube_music = self._is_youtube_music(window_title)
            
            # Check if it's educational
            self.is_educational = self._is_educational_content(window_title)
            
            # Determine if it's a distraction
            is_distraction, dist_type = self._check_distraction(window_title, process_name)
            
            # Update state based on detection
            if is_distraction:
                self._handle_distraction_detected(dist_type, window_title, process_name)
            else:
                self._handle_focus_restored(window_title, process_name)
            
            self.current_activity = {
                "window_title": window_title,
                "process": process_name,
                "is_distraction": is_distraction,
                "distraction_type": dist_type if is_distraction else None,
                "is_youtube": self.is_youtube,
                "is_youtube_shorts": self.is_youtube_shorts,
                "is_youtube_music": self.is_youtube_music,
                "is_educational": self.is_educational,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error checking window: {e}")
    
    def _handle_distraction_detected(self, dist_type: str, window_title: str, process_name: str):
        """Handle when a distraction is detected"""
        if not self.distraction_detected:
            # New distraction detected
            self.distraction_detected = True
            self.distraction_start_time = time.time()
            self.distraction_type = dist_type
            logger.info(f"Distraction detected: {dist_type} - {window_title}")
            
            # Immediate alert for YouTube Shorts and Music
            if 'shorts' in dist_type.lower() or 'music' in dist_type.lower():
                self._trigger_alert("distraction", f"🚫 {dist_type.upper()} detected! Focus on your work!", {
                    "window": window_title,
                    "process": process_name,
                    "type": dist_type
                })
        else:
            # Check if alert threshold exceeded
            if time.time() - self.distraction_start_time >= self.alert_threshold:
                current_time = time.time()
                if current_time - self.last_alert_time >= self.alert_cooldown:
                    self._trigger_alert("distraction", f"⚠️ Still on {self.distraction_type}! Get back to work!", {
                        "window": window_title,
                        "process": process_name,
                        "type": self.distraction_type,
                        "duration": time.time() - self.distraction_start_time
                    })
                    self.last_alert_time = current_time
    
    def _handle_focus_restored(self, window_title: str, process_name: str):
        """Handle when focus is restored"""
        if self.distraction_detected:
            logger.info(f"Focus restored - window: {window_title}")
            self._reset_distraction_state()
            self._trigger_alert("focus_restored", "✅ Focus restored! Keep going! 💪", {
                "window": window_title,
                "process": process_name
            })
    
    def _reset_distraction_state(self):
        """Reset distraction state"""
        self.distraction_detected = False
        self.distraction_start_time = None
        self.distraction_type = None
        self.is_youtube = False
        self.is_youtube_shorts = False
        self.is_youtube_music = False
        self.is_educational = False
        self.window_closed_time = None
    
    def _get_active_process_name(self) -> str:
        """Get active process name"""
        try:
            active_window = gw.getActiveWindow()
            if active_window:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        proc_name = proc.info['name'].lower()
                        browsers = ['chrome', 'firefox', 'edge', 'brave', 'opera', 'vivaldi']
                        if any(x in proc_name for x in browsers):
                            return proc.info['name']
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            return "unknown"
        except:
            return "unknown"
    
    def _is_youtube(self, window_title: str, process_name: str) -> bool:
        """Check if it's YouTube"""
        if not window_title:
            return False
        return 'youtube' in window_title.lower() or 'youtu.be' in window_title.lower()
    
    def _is_youtube_shorts(self, window_title: str) -> bool:
        """Check if it's YouTube Shorts"""
        if not window_title:
            return False
        # Check for shorts in title
        shorts_patterns = ['shorts', 'short', '/shorts/', 'shorts/']
        return any(pattern in window_title.lower() for pattern in shorts_patterns)
    
    def _is_youtube_music(self, window_title: str) -> bool:
        """Check if it's YouTube Music"""
        if not window_title:
            return False
        # Check for music in title
        music_patterns = ['music.youtube', 'youtube music', 'music - youtube', 'youtube.com/music']
        return any(pattern in window_title.lower() for pattern in music_patterns)
    
    def _is_educational_content(self, window_title: str) -> bool:
        """Check if the content is educational"""
        if not window_title:
            return False
        
        window_lower = window_title.lower()
        
        # Check educational keywords
        for keyword in self.educational_keywords:
            if keyword in window_lower:
                return True
        
        # Check educational channels
        for channel in self.educational_channels:
            if channel in window_lower:
                return True
        
        return False
    
    def _check_distraction(self, window_title: str, process_name: str) -> tuple:
        """Check if window contains distraction content"""
        if not window_title:
            return False, None
        
        window_lower = window_title.lower()
        
        # Check if it's YouTube Music - ALWAYS a distraction
        if self._is_youtube_music(window_title):
            return True, "youtube_music"
        
        # Check if it's YouTube Shorts - ALWAYS a distraction
        if self._is_youtube_shorts(window_title):
            return True, "youtube_shorts"
        
        # If it's YouTube (not shorts/music), check if educational
        if self._is_youtube(window_title, ""):
            # Check if educational
            if self._is_educational_content(window_title):
                return False, None  # Allow educational YouTube
            
            # Check for educational channels in title
            for channel in self.educational_channels:
                if channel in window_lower:
                    return False, None
            
            # If not educational, it's a distraction
            return True, "youtube_video"
        
        # Check other distraction patterns
        for dist_type, patterns in self.distraction_patterns.items():
            for pattern in patterns:
                if pattern.lower() in window_lower:
                    # Skip if it's educational
                    if self._is_educational_content(window_title):
                        return False, None
                    return True, dist_type
        
        return False, None
    
    def _trigger_alert(self, alert_type: str, message: str, details: Dict[str, Any]):
        """Trigger alert"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, message, details)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback for alerts"""
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop screen monitoring"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
            self.monitoring_thread = None
        
        # Reset state
        self._reset_distraction_state()
        
        logger.info("Screen monitoring stopped")
        return {"status": "success", "message": "Screen monitoring stopped"}
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_running": self.is_running,
            "is_available": self.is_available,
            "distraction_detected": self.distraction_detected,
            "distraction_type": self.distraction_type,
            "distraction_duration": time.time() - self.distraction_start_time if self.distraction_start_time else 0,
            "current_activity": self.current_activity,
            "is_educational": self.is_educational,
            "is_youtube": self.is_youtube,
            "is_youtube_shorts": self.is_youtube_shorts,
            "is_youtube_music": self.is_youtube_music
        }