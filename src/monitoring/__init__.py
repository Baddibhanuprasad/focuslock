# src/monitoring/__init__.py
"""Monitoring module for webcam and screen"""

from .webcam_monitor import WebcamMonitor
from .screen_monitor import ScreenMonitor
from .activity_detector import ActivityDetector
from .media_controllers import MediaController

__all__ = ['WebcamMonitor', 'ScreenMonitor', 'ActivityDetector', 'MediaController']