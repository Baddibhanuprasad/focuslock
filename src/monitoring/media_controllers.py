# src/monitoring/media_controllers.py
"""Media controllers for YouTube and other platforms"""

import time
from typing import Dict, Any
import logging
import subprocess

logger = logging.getLogger(__name__)

try:
    import pyautogui
except ImportError:
    pyautogui = None
    logger.warning("pyautogui is not installed; media control is unavailable")

class MediaController:
    """Control media playback on various platforms"""
    
    def __init__(self):
        self.is_paused = False
        self.is_available = pyautogui is not None
        self.last_pause_time = None
        self.youtube_tab_found = False
    
    def pause_youtube(self) -> Dict[str, Any]:
        """Pause YouTube video"""
        try:
            if not self.is_available:
                return {"status": "error", "message": "pyautogui is not installed; media control is unavailable"}

            if not self.detect_youtube_tab():
                return {"status": "no_action", "message": "Active window is not YouTube"}

            # Method 1: Send space key
            pyautogui.press('space')
            time.sleep(0.1)
            
            # Method 2: Click on video area
            screen_width, screen_height = pyautogui.size()
            pyautogui.click(screen_width // 2, screen_height // 2 - 50)
            
            self.is_paused = True
            self.last_pause_time = time.time()
            
            logger.info("YouTube paused")
            return {"status": "success", "message": "YouTube paused"}
            
        except Exception as e:
            logger.error(f"Error pausing YouTube: {e}")
            return {"status": "error", "message": str(e)}
    
    def resume_youtube(self) -> Dict[str, Any]:
        """Resume YouTube video"""
        try:
            if not self.is_available:
                return {"status": "error", "message": "pyautogui is not installed; media control is unavailable"}

            pyautogui.press('space')
            time.sleep(0.1)
            
            self.is_paused = False
            
            logger.info("YouTube resumed")
            return {"status": "success", "message": "YouTube resumed"}
            
        except Exception as e:
            logger.error(f"Error resuming YouTube: {e}")
            return {"status": "error", "message": str(e)}
    
    def detect_youtube_tab(self) -> bool:
        """Detect if YouTube is active"""
        try:
            import pygetwindow as gw
            active_window = gw.getActiveWindow()
            
            if active_window and 'YouTube' in active_window.title:
                self.youtube_tab_found = True
                return True
            
            self.youtube_tab_found = False
            return False
            
        except Exception as e:
            logger.error(f"Error detecting YouTube: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get controller status"""
        return {
            "is_paused": self.is_paused,
            "is_available": self.is_available,
            "youtube_tab_found": self.youtube_tab_found,
            "last_pause_time": self.last_pause_time
        }