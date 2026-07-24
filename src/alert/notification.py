# src/alert/notification.py
"""System notifications with centered popup - Fixed"""

import platform
import subprocess
import logging
from typing import Optional
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading
import time
import queue

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manage system notifications"""
    
    def __init__(self):
        self.system = platform.system()
        self.notifications_enabled = True
        self.popup_active = False
        self.current_popup = None
        self.popup_queue = queue.Queue()
        self.popup_thread = None
        self.running = True
        
        # Start popup handler thread
        self.popup_thread = threading.Thread(target=self._popup_handler)
        self.popup_thread.daemon = True
        self.popup_thread.start()
    
    def _popup_handler(self):
        """Handle popup creation in a dedicated thread"""
        while self.running:
            try:
                # Get popup request from queue
                popup_data = self.popup_queue.get(timeout=0.1)
                if popup_data:
                    title, message, notification_type = popup_data
                    self._create_popup_window(title, message, notification_type)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Popup handler error: {e}")
    
    def show_notification(self, title: str, message: str, notification_type: str = "info"):
        """Show a system notification"""
        if not self.notifications_enabled:
            return
        
        logger.info(f"Notification: {title} - {message}")
        
        # Show centered popup for important alerts
        if notification_type in ["warning", "distraction"]:
            # Add to queue for thread-safe popup creation
            self.popup_queue.put((title, message, notification_type))
        
        # Also show system notification
        try:
            if self.system == "Windows":
                self._windows_notification(title, message)
            elif self.system == "Darwin":
                self._mac_notification(title, message)
            elif self.system == "Linux":
                self._linux_notification(title, message)
            else:
                print(f"\n🔔 {title}\n{message}\n")
        except Exception as e:
            logger.error(f"Notification error: {e}")
    
    def _create_popup_window(self, title: str, message: str, notification_type: str):
        """Create the popup window - centered on screen"""
        try:
            # Close existing popup if any
            self._close_popup()
            
            # Create root window
            root = tk.Tk()
            root.title("Focus Alert")
            
            # Get screen dimensions
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            
            # Set window size (not full screen)
            window_width = 600
            window_height = 400
            
            # Calculate position to center
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Set window geometry (width x height + x + y)
            root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Make it always on top but not full screen
            root.attributes('-topmost', True)
            root.attributes('-alpha', 0.95)
            root.configure(bg='#1a1a2e')
            
            # Remove window decorations
            root.overrideredirect(True)
            
            # Add a border frame
            border_frame = tk.Frame(root, bg='#00d4ff', bd=2)
            border_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Main content frame
            main_frame = tk.Frame(border_frame, bg='#1a1a2e')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Alert icon/emoji
            icon = "⚠️" if notification_type == "warning" else "🚫"
            icon_label = tk.Label(
                main_frame,
                text=icon,
                font=('Arial', 48),
                fg='#ff4444',
                bg='#1a1a2e'
            )
            icon_label.pack(pady=10)
            
            # Title
            title_label = tk.Label(
                main_frame,
                text=title,
                font=('Arial', 24, 'bold'),
                fg='#ff4444',
                bg='#1a1a2e'
            )
            title_label.pack(pady=10)
            
            # Message
            msg_label = tk.Label(
                main_frame,
                text=message,
                font=('Arial', 14),
                fg='#ffffff',
                bg='#1a1a2e',
                wraplength=500,
                justify='center'
            )
            msg_label.pack(pady=15)
            
            # Action buttons frame
            button_frame = tk.Frame(main_frame, bg='#1a1a2e')
            button_frame.pack(pady=20)
            
            # Focus button (primary)
            focus_btn = tk.Button(
                button_frame,
                text="🎯 I'M FOCUSED!",
                font=('Arial', 14, 'bold'),
                bg='#00d4ff',
                fg='#1a1a2e',
                padx=25,
                pady=10,
                command=lambda: self._close_popup(root)
            )
            focus_btn.pack(side=tk.LEFT, padx=10)
            
            # Close button (secondary)
            close_btn = tk.Button(
                button_frame,
                text="✕ Close",
                font=('Arial', 12),
                bg='#ff4444',
                fg='#ffffff',
                padx=15,
                pady=8,
                command=lambda: self._close_popup(root)
            )
            close_btn.pack(side=tk.LEFT, padx=10)
            
            # Bind escape key to close
            root.bind('<Escape>', lambda e: self._close_popup(root))
            
            # Make window draggable
            def start_move(event):
                root.x = event.x
                root.y = event.y
            
            def stop_move(event):
                root.x = None
                root.y = None
            
            def do_move(event):
                if hasattr(root, 'x') and root.x is not None:
                    deltax = event.x - root.x
                    deltay = event.y - root.y
                    x = root.winfo_x() + deltax
                    y = root.winfo_y() + deltay
                    root.geometry(f"+{x}+{y}")
            
            # Bind drag events to the border frame
            border_frame.bind('<Button-1>', start_move)
            border_frame.bind('<B1-Motion>', do_move)
            border_frame.bind('<ButtonRelease-1>', stop_move)
            
            # Also bind to title area
            title_label.bind('<Button-1>', start_move)
            title_label.bind('<B1-Motion>', do_move)
            title_label.bind('<ButtonRelease-1>', stop_move)
            
            # Store reference
            self.popup_active = True
            self.current_popup = root
            
            # Schedule the close on the popup's Tk thread. Tk widgets must
            # not be destroyed by the sound or monitoring worker threads.
            root.after(20000, lambda: self._close_popup(root))
            
            # Start main loop
            root.mainloop()
            
        except Exception as e:
            logger.error(f"Error creating popup: {e}")
            self.popup_active = False
            self.current_popup = None
    
    def _close_popup(self, root=None):
        """Close the popup window safely"""
        self.popup_active = False

        popup = root or self.current_popup
        if popup is None:
            return

        # Calls can originate from monitoring/sound threads. Marshal the
        # actual Tk operation back to the thread that owns the popup.
        if threading.current_thread() is not self.popup_thread:
            try:
                popup.after(0, lambda: self._close_popup(popup))
            except tk.TclError:
                self.current_popup = None
            return

        try:
            popup.quit()
            popup.destroy()
        except tk.TclError:
            pass

        if self.current_popup is popup:
            self.current_popup = None
    
    def _windows_notification(self, title: str, message: str):
        """Show Windows notification"""
        try:
            # Try win10toast
            try:
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(
                    title, 
                    message, 
                    duration=5, 
                    threaded=True
                )
                return
            except ImportError:
                pass
            
            # Fallback: Use PowerShell
            try:
                import subprocess
                script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $notification = New-Object System.Windows.Forms.NotifyIcon
                $notification.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -Id $pid).Path)
                $notification.BalloonTipTitle = "{title}"
                $notification.BalloonTipText = "{message}"
                $notification.Visible = $True
                $notification.ShowBalloonTip(5000)
                '''
                subprocess.run(["powershell", "-Command", script], capture_output=True)
            except:
                logger.info(f"Windows Notification: {title} - {message}")
                
        except Exception as e:
            logger.error(f"Windows notification error: {e}")
            logger.info(f"Notification: {title} - {message}")
    
    def _mac_notification(self, title: str, message: str):
        """Show macOS notification"""
        try:
            command = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", command], check=True)
        except Exception as e:
            logger.error(f"Mac notification error: {e}")
    
    def _linux_notification(self, title: str, message: str):
        """Show Linux notification"""
        try:
            subprocess.run(
                ["notify-send", title, message],
                check=True,
                capture_output=True
            )
        except Exception as e:
            logger.error(f"Linux notification error: {e}")
    
    def enable_notifications(self, enabled: bool):
        """Enable or disable notifications"""
        self.notifications_enabled = enabled
    
    def close_all_popups(self):
        """Close all active popups"""
        self._close_popup()
        self.popup_active = False
    
    def stop(self):
        """Stop the notification manager"""
        self.running = False
        self.close_all_popups()