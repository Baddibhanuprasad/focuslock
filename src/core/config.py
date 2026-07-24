# src/core/config.py
"""Configuration management"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict

@dataclass
class AppConfig:
    """Application configuration"""
    # Focus settings
    default_focus_duration: int = 25  # minutes
    break_duration: int = 5  # minutes
    long_break_duration: int = 15  # minutes
    sessions_before_long_break: int = 4
    
    # Monitoring settings
    webcam_enabled: bool = True
    screen_monitoring_enabled: bool = True
    sleep_detection_enabled: bool = True
    entertainment_detection_enabled: bool = True
    
    # Alert settings
    sound_enabled: bool = True
    alert_duration: int = 30  # seconds
    task_timeout: int = 30  # seconds
    
    # Thresholds
    sleep_detection_threshold: int = 30  # seconds
    absence_threshold: int = 60  # seconds
    entertainment_threshold: int = 10  # seconds
    
    # YouTube settings
    auto_pause_youtube: bool = True
    auto_resume_youtube: bool = True
    
    # UI settings
    theme: str = "dark"
    language: str = "en"
    show_notifications: bool = True
    
    # Privacy settings
    save_webcam_images: bool = False
    anonymize_data: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create config from dictionary"""
        return cls(**data)

class ConfigManager:
    """Manage application configuration"""
    
    def __init__(self, config_path: str = "data/config/settings.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    return AppConfig.from_dict(data)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Create default config
        default_config = AppConfig()
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: AppConfig):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self._save_config(self.config)
            return True
        return False
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self._save_config(self.config)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = AppConfig()
        self._save_config(self.config)