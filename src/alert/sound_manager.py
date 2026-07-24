# src/alert/sound_manager.py
"""Sound management with custom sound support"""

import os
import threading
from typing import Optional
import logging
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

logger = logging.getLogger(__name__)

class SoundManager:
    """Manage sound playback"""
    
    def __init__(self):
        self.sound_enabled = True
        self.sounds = {}
        self.custom_sound = None
        self.custom_channel = None
        self._init_sounds()
    
    def _init_sounds(self):
        """Initialize sounds"""
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
            except Exception as e:
                logger.error(f"Could not initialize pygame mixer: {e}")
            self._load_sounds()
    
    def _load_sounds(self):
        """Load sound files"""
        sound_dir = Path("gui/resources/sounds")
        sound_dir.mkdir(parents=True, exist_ok=True)
        
        # Define sound files
        sound_files = {
            "alert": ["alert.wav", "alert.mp3"],
            "wake_up": ["wake_up.wav", "wake_up.mp3"],
            "focus_lost": ["focus_lost.wav", "focus_lost.mp3"],
            "timer_end": ["timer_end.wav", "timer_end.mp3"],
            "success": ["success.wav", "success.mp3"]
        }
        
        loaded_count = 0
        for name, filenames in sound_files.items():
            for filename in filenames:
                filepath = sound_dir / filename
                if filepath.exists() and PYGAME_AVAILABLE:
                    try:
                        if filepath.stat().st_size > 100:
                            self.sounds[name] = pygame.mixer.Sound(str(filepath))
                            logger.info(f"Loaded sound: {name} from {filename}")
                            loaded_count += 1
                            break
                        else:
                            logger.warning(f"Sound file {filename} is too small, skipping")
                    except Exception as e:
                        logger.error(f"Error loading sound {name} from {filename}: {e}")
        
        if loaded_count == 0:
            logger.warning("No sound files loaded, using system beeps")
    
    def play_custom_sound(self, sound_path: str):
        """Play a custom sound file"""
        if not self.sound_enabled:
            return
        
        try:
            # Check if custom sound exists
            if Path(sound_path).exists():
                if PYGAME_AVAILABLE:
                    try:
                        sound = pygame.mixer.Sound(sound_path)
                        self.custom_channel = sound.play()
                        return
                    except Exception as e:
                        logger.error(f"Error playing custom sound: {e}")
            
            # Fallback to default
            self.play_alert_sound("alert")
            
        except Exception as e:
            logger.error(f"Custom sound error: {e}")
            self._beep("alert")

    def stop_custom_sound(self):
        """Stop the currently playing custom sound, if any."""
        if self.custom_channel is not None:
            try:
                self.custom_channel.stop()
            except Exception as e:
                logger.error(f"Error stopping custom sound: {e}")
            finally:
                self.custom_channel = None
    
    def play_alert_sound(self, sound_type: str = "alert"):
        """Play an alert sound"""
        if not self.sound_enabled:
            return
        
        try:
            # Try to play loaded sound
            if sound_type in self.sounds and PYGAME_AVAILABLE:
                try:
                    self.sounds[sound_type].play()
                    return
                except Exception as e:
                    logger.error(f"Error playing sound {sound_type}: {e}")
            
            # Fallback to beep
            self._beep(sound_type)
            
        except Exception as e:
            logger.error(f"Sound playback error: {e}")
            try:
                self._beep(sound_type)
            except:
                print(f"\n🔔 {sound_type.upper()} ALERT!\n")
    
    def _beep(self, sound_type: str):
        """Generate beep sounds"""
        try:
            if WINSOUND_AVAILABLE:
                if sound_type == "alert":
                    winsound.Beep(440, 300)
                elif sound_type == "wake_up":
                    for _ in range(3):
                        winsound.Beep(880, 200)
                        threading.Event().wait(0.2)
                elif sound_type == "focus_lost":
                    winsound.Beep(330, 300)
                    threading.Event().wait(0.1)
                    winsound.Beep(440, 300)
                elif sound_type == "timer_end":
                    for _ in range(5):
                        winsound.Beep(660, 100)
                        threading.Event().wait(0.1)
                elif sound_type == "success":
                    winsound.Beep(523, 200)
                    threading.Event().wait(0.1)
                    winsound.Beep(659, 200)
                else:
                    winsound.Beep(440, 300)
            else:
                print(f"\n🔔 {sound_type.upper()} ALERT!\n")
        except:
            print(f"\n🔔 {sound_type.upper()} ALERT!\n")
    
    def enable_sound(self, enabled: bool):
        """Enable or disable sound"""
        self.sound_enabled = enabled