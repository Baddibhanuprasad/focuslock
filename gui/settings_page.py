# gui/settings_page.py
"""Settings page for the application"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.config import ConfigManager

class SettingsPage:
    """Settings configuration page"""
    
    def __init__(self, parent):
        self.parent = parent
        self.config = ConfigManager()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings UI"""
        # Main frame
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            frame,
            text="⚙️ Settings",
            font=('Arial', 20, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title.pack(pady=10)
        
        # Focus settings
        focus_frame = tk.LabelFrame(frame, text="Focus Settings", bg='#1a1a2e', fg='white')
        focus_frame.pack(fill=tk.X, pady=10)
        
        # Default duration
        duration_frame = tk.Frame(focus_frame, bg='#1a1a2e')
        duration_frame.pack(pady=5, padx=10)
        
        tk.Label(
            duration_frame,
            text="Default Duration (minutes):",
            bg='#1a1a2e',
            fg='white'
        ).pack(side=tk.LEFT)
        
        self.duration_var = tk.StringVar(value=str(self.config.get('default_focus_duration', 25)))
        tk.Spinbox(
            duration_frame,
            from_=5,
            to=120,
            width=10,
            textvariable=self.duration_var
        ).pack(side=tk.LEFT, padx=10)
        
        # Monitoring settings
        monitor_frame = tk.LabelFrame(frame, text="Monitoring Settings", bg='#1a1a2e', fg='white')
        monitor_frame.pack(fill=tk.X, pady=10)
        
        # Webcam
        self.webcam_var = tk.BooleanVar(value=self.config.get('webcam_enabled', True))
        tk.Checkbutton(
            monitor_frame,
            text="Enable Webcam Monitoring",
            variable=self.webcam_var,
            bg='#1a1a2e',
            fg='white',
            selectcolor='#1a1a2e'
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # Screen monitoring
        self.screen_var = tk.BooleanVar(value=self.config.get('screen_monitoring_enabled', True))
        tk.Checkbutton(
            monitor_frame,
            text="Enable Screen Monitoring",
            variable=self.screen_var,
            bg='#1a1a2e',
            fg='white',
            selectcolor='#1a1a2e'
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # Sleep detection
        self.sleep_var = tk.BooleanVar(value=self.config.get('sleep_detection_enabled', True))
        tk.Checkbutton(
            monitor_frame,
            text="Enable Sleep Detection",
            variable=self.sleep_var,
            bg='#1a1a2e',
            fg='white',
            selectcolor='#1a1a2e'
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # Entertainment detection
        self.entertainment_var = tk.BooleanVar(value=self.config.get('entertainment_detection_enabled', True))
        tk.Checkbutton(
            monitor_frame,
            text="Enable Entertainment Detection",
            variable=self.entertainment_var,
            bg='#1a1a2e',
            fg='white',
            selectcolor='#1a1a2e'
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # YouTube settings
        youtube_frame = tk.LabelFrame(frame, text="YouTube Settings", bg='#1a1a2e', fg='white')
        youtube_frame.pack(fill=tk.X, pady=10)
        
        self.youtube_pause_var = tk.BooleanVar(value=self.config.get('auto_pause_youtube', True))
        tk.Checkbutton(
            youtube_frame,
            text="Auto-pause YouTube when away",
            variable=self.youtube_pause_var,
            bg='#1a1a2e',
            fg='white',
            selectcolor='#1a1a2e'
        ).pack(anchor=tk.W, padx=20, pady=5)
        
        # Save button
        save_btn = tk.Button(
            frame,
            text="💾 Save Settings",
            font=('Arial', 12),
            bg='#00d4ff',
            fg='#1a1a2e',
            padx=20,
            pady=10,
            command=self.save_settings
        )
        save_btn.pack(pady=20)
        
        # Reset button
        reset_btn = tk.Button(
            frame,
            text="↻ Reset to Defaults",
            font=('Arial', 10),
            bg='#ffd700',
            fg='#1a1a2e',
            padx=20,
            pady=5,
            command=self.reset_settings
        )
        reset_btn.pack(pady=5)
    
    def save_settings(self):
        """Save settings"""
        try:
            updates = {
                'default_focus_duration': int(self.duration_var.get()),
                'webcam_enabled': self.webcam_var.get(),
                'screen_monitoring_enabled': self.screen_var.get(),
                'sleep_detection_enabled': self.sleep_var.get(),
                'entertainment_detection_enabled': self.entertainment_var.get(),
                'auto_pause_youtube': self.youtube_pause_var.get()
            }
            
            self.config.update(updates)
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            self.config.reset_to_defaults()
            self.duration_var.set(str(self.config.get('default_focus_duration', 25)))
            self.webcam_var.set(self.config.get('webcam_enabled', True))
            self.screen_var.set(self.config.get('screen_monitoring_enabled', True))
            self.sleep_var.set(self.config.get('sleep_detection_enabled', True))
            self.entertainment_var.set(self.config.get('entertainment_detection_enabled', True))
            self.youtube_pause_var.set(self.config.get('auto_pause_youtube', True))
            messagebox.showinfo("Success", "Settings reset to defaults!")