# gui/main_window.py
"""Main GUI window using Tkinter"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from pathlib import Path
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import the application
try:
    from app import FocusApplication
except ImportError as e:
    print(f"Error importing app: {e}")
    print(f"Current sys.path: {sys.path}")
    # Try alternative import
    try:
        from src.app import FocusApplication
    except ImportError:
        print("Could not import FocusApplication. Please check the path.")
        sys.exit(1)

class FocusAppGUI:
    """Main GUI application"""

    COLORS = {
        'background': '#0b1220',
        'surface': '#111c2e',
        'surface_light': '#182840',
        'text': '#f8fafc',
        'muted': '#94a3b8',
        'accent': '#38bdf8',
        'accent_dark': '#082f49',
        'success': '#4ade80',
        'warning': '#fbbf24',
        'danger': '#fb7185',
    }
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Focus Mode | Deep work, made visible")
        self.root.geometry("900x720")
        self.root.minsize(720, 620)
        self.root.configure(bg=self.COLORS['background'])
        
        # Initialize application
        try:
            self.app = FocusApplication()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize application: {e}")
            self.root.destroy()
            return
        
        # Setup UI
        self.setup_ui()
        
        # Start update loop
        self.update_status()
        
    def setup_ui(self):
        """Setup the user interface"""
        colors = self.COLORS
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TProgressbar',
            background=colors['accent'],
            troughcolor=colors['surface_light'],
            bordercolor=colors['surface_light'],
            lightcolor=colors['accent'],
            darkcolor=colors['accent'],
            thickness=12
        )

        self.page_container = tk.Frame(self.root, bg=colors['background'])
        self.page_container.pack(fill=tk.BOTH, expand=True)

        self.home_frame = tk.Frame(self.page_container, bg=colors['background'])
        self.focus_frame = tk.Frame(self.page_container, bg=colors['background'])

        self.setup_home_page()
        self.show_home_page()

        # The focus page owns the existing timer and monitoring controls.
        main_frame = tk.Frame(self.focus_frame, bg=colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=34, pady=28)

        header = tk.Frame(main_frame, bg=colors['background'])
        header.pack(fill=tk.X, pady=(0, 22))

        tk.Button(
            header,
            text="<  HOME",
            font=('Segoe UI', 9, 'bold'),
            fg=colors['muted'],
            bg=colors['background'],
            activebackground=colors['background'],
            activeforeground=colors['text'],
            relief=tk.FLAT,
            bd=0,
            command=self.show_home_page
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="FOCUS MODE / DEEP WORK TIMER",
            font=('Segoe UI', 9, 'bold'),
            fg=colors['accent'],
            bg=colors['background']
        ).pack(anchor=tk.W)
        
        # Title
        title_label = tk.Label(
            header,
            text="Make room for your best work.",
            font=('Segoe UI', 25, 'bold'),
            fg=colors['text'],
            bg=colors['background']
        )
        title_label.pack(anchor=tk.W, pady=(5, 2))

        tk.Label(
            header,
            text="Set a rhythm, stay present, and let the timer hold the line.",
            font=('Segoe UI', 11),
            fg=colors['muted'],
            bg=colors['background']
        ).pack(anchor=tk.W)
        
        # Timer display
        self.timer_frame = tk.Frame(
            main_frame, bg=colors['surface'], highlightthickness=1,
            highlightbackground='#203451', padx=28, pady=24
        )
        self.timer_frame.pack(fill=tk.X, pady=(0, 18))
        
        self.timer_label = tk.Label(
            self.timer_frame,
            text="00:00",
            font=('Segoe UI', 58, 'bold'),
            fg=colors['text'],
            bg=colors['surface']
        )
        self.timer_label.pack()

        tk.Label(
            self.timer_frame,
            text="TIME LEFT IN THIS SESSION",
            font=('Segoe UI', 9, 'bold'),
            fg=colors['muted'],
            bg=colors['surface']
        ).pack(pady=(0, 12))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            length=400,
            mode='determinate',
            style='TProgressbar'
        )
        self.progress.pack(fill=tk.X, pady=(0, 18))
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="READY WHEN YOU ARE",
            font=('Segoe UI', 11, 'bold'),
            fg=colors['muted'],
            bg=colors['background']
        )
        self.status_label.pack(pady=(0, 14))
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg=colors['background'])
        button_frame.pack(pady=(0, 20))
        
        # Start button
        self.start_btn = tk.Button(
            button_frame,
            text="START SESSION",
            font=('Segoe UI', 10, 'bold'),
            bg=colors['accent'],
            fg=colors['accent_dark'],
            activebackground='#7dd3fc',
            activeforeground=colors['accent_dark'],
            relief=tk.FLAT, bd=0, padx=24, pady=12,
            command=self.start_session
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        # Pause button
        self.pause_btn = tk.Button(
            button_frame,
            text="PAUSE",
            font=('Segoe UI', 10, 'bold'),
            bg=colors['warning'],
            fg='#422006',
            activebackground='#fcd34d',
            relief=tk.FLAT, bd=0, padx=24, pady=12,
            command=self.pause_session,
            state=tk.DISABLED
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_btn = tk.Button(
            button_frame,
            text="STOP",
            font=('Segoe UI', 10, 'bold'),
            bg=colors['danger'],
            fg='#4c0519',
            activebackground='#fda4af',
            relief=tk.FLAT, bd=0, padx=24, pady=12,
            command=self.stop_session,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Duration selector
        duration_frame = tk.Frame(main_frame, bg=colors['background'])
        duration_frame.pack(pady=10)
        
        tk.Label(
            duration_frame,
            text="SESSION LENGTH",
            font=('Segoe UI', 9, 'bold'),
            fg=colors['muted'],
            bg=colors['background']
        ).pack(side=tk.LEFT, padx=5)
        
        self.duration_var = tk.StringVar(value="25")
        self.duration_spinbox = tk.Spinbox(
            duration_frame,
            from_=5,
            to=120,
            width=10,
            textvariable=self.duration_var,
            font=('Segoe UI', 11),
            bg=colors['surface_light'],
            fg=colors['text'],
            buttonbackground=colors['surface_light'],
            relief=tk.FLAT,
            bd=0
        )
        self.duration_spinbox.pack(side=tk.LEFT, padx=5)
        
        # Status info frame
        info_frame = tk.Frame(main_frame, bg=colors['surface'], padx=14, pady=12)
        info_frame.pack(pady=(6, 18), fill=tk.X)
        
        # Webcam status
        self.webcam_status = tk.Label(
            info_frame,
            text="📷 Webcam: Off",
            font=('Segoe UI', 10),
            fg=colors['muted'],
            bg=colors['surface']
        )
        self.webcam_status.pack(side=tk.LEFT, padx=10)
        
        # Screen status
        self.screen_status = tk.Label(
            info_frame,
            text="🖥️ Screen: Off",
            font=('Segoe UI', 10),
            fg=colors['muted'],
            bg=colors['surface']
        )
        self.screen_status.pack(side=tk.LEFT, padx=10)
        
        # User status
        self.user_status = tk.Label(
            info_frame,
            text="👤 User: Unknown",
            font=('Segoe UI', 10),
            fg=colors['muted'],
            bg=colors['surface']
        )
        self.user_status.pack(side=tk.LEFT, padx=10)
        
        # Task display (for wake-up tasks)
        self.task_frame = tk.Frame(main_frame, bg=colors['background'])
        self.task_frame.pack(pady=10, fill=tk.X)
        
        self.task_label = tk.Label(
            self.task_frame,
            text="",
            font=('Segoe UI', 11, 'bold'),
            fg=colors['warning'],
            bg=colors['background'],
            wraplength=600
        )
        self.task_label.pack()
        
        # Task input (for wake-up tasks)
        task_input_frame = tk.Frame(main_frame, bg=colors['background'])
        task_input_frame.pack(pady=5)
        
        self.task_entry = tk.Entry(
            task_input_frame,
            font=('Segoe UI', 11),
            width=30,
            bg=colors['surface_light'],
            fg=colors['text'],
            insertbackground=colors['text'],
            relief=tk.FLAT,
            bd=0,
            state=tk.DISABLED
        )
        self.task_entry.pack(side=tk.LEFT, padx=5)
        
        self.task_submit_btn = tk.Button(
            task_input_frame,
            text="VERIFY",
            font=('Segoe UI', 9, 'bold'),
            bg=colors['accent'],
            fg=colors['accent_dark'],
            activebackground='#7dd3fc',
            relief=tk.FLAT,
            bd=0,
            padx=14,
            pady=8,
            command=self.submit_task,
            state=tk.DISABLED
        )
        self.task_submit_btn.pack(side=tk.LEFT, padx=5)

    def setup_home_page(self):
        """Build the landing page for the desktop application."""
        colors = self.COLORS
        content = tk.Frame(self.home_frame, bg=colors['background'])
        content.pack(fill=tk.BOTH, expand=True, padx=54, pady=54)

        tk.Label(
            content,
            text="FOCUS MODE",
            font=('Segoe UI', 11, 'bold'),
            fg=colors['accent'],
            bg=colors['background']
        ).pack(anchor=tk.W, pady=(50, 8))

        tk.Label(
            content,
            text="Protect your attention.",
            font=('Segoe UI', 34, 'bold'),
            fg=colors['text'],
            bg=colors['background']
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text="A calm study timer with webcam awareness, screen monitoring,\nand gentle accountability when your focus drifts.",
            font=('Segoe UI', 13),
            justify=tk.LEFT,
            fg=colors['muted'],
            bg=colors['background']
        ).pack(anchor=tk.W, pady=(14, 30))

        focus_button = tk.Button(
            content,
            text="OPEN FOCUS MODE  >",
            font=('Segoe UI', 11, 'bold'),
            bg=colors['accent'],
            fg=colors['accent_dark'],
            activebackground='#7dd3fc',
            activeforeground=colors['accent_dark'],
            relief=tk.FLAT,
            bd=0,
            padx=28,
            pady=14,
            command=self.show_focus_page
        )
        focus_button.pack(anchor=tk.W)

        features = tk.Frame(content, bg=colors['background'])
        features.pack(fill=tk.X, pady=(74, 0))
        for title, description in (
            ('WEBCAM AWARE', 'Detects absence and sleepiness'),
            ('SCREEN GUARD', 'Flags entertainment distractions'),
            ('YOUTUBE ONLY', 'Pauses YouTube when you step away'),
        ):
            item = tk.Frame(features, bg=colors['surface'], padx=16, pady=14)
            item.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            tk.Label(item, text=title, font=('Segoe UI', 9, 'bold'), fg=colors['accent'], bg=colors['surface']).pack(anchor=tk.W)
            tk.Label(item, text=description, font=('Segoe UI', 10), fg=colors['muted'], bg=colors['surface'], wraplength=180, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 0))

    def show_home_page(self):
        """Show the application home page."""
        self.focus_frame.pack_forget()
        self.home_frame.pack(fill=tk.BOTH, expand=True)

    def show_focus_page(self):
        """Show the focus timer and monitoring controls."""
        self.home_frame.pack_forget()
        self.focus_frame.pack(fill=tk.BOTH, expand=True)
        
    def start_session(self):
        """Start a focus session"""
        try:
            duration = int(self.duration_var.get())
            result = self.app.start_focus_session(duration)
            
            if result['status'] == 'success':
                self.start_btn.config(state=tk.DISABLED)
                self.pause_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.NORMAL)
                self.duration_spinbox.config(state=tk.DISABLED)
                self.status_label.config(text="▶ Running", fg='#00ff00')
                
                # Enable task input if needed
                if self.app.alert_system.get_active_task():
                    self.task_entry.config(state=tk.NORMAL)
                    self.task_submit_btn.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", result.get('message', 'Failed to start session'))
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid duration")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def pause_session(self):
        """Pause the current session"""
        result = self.app.pause_focus_session()
        if result['status'] == 'success':
            self.pause_btn.config(text="▶ Resume", command=self.resume_session)
            self.status_label.config(text="⏸ Paused", fg='#ffd700')
        else:
            messagebox.showerror("Error", result.get('message', 'Failed to pause session'))
    
    def resume_session(self):
        """Resume the current session"""
        result = self.app.resume_focus_session()
        if result['status'] == 'success':
            self.pause_btn.config(text="⏸ Pause", command=self.pause_session)
            self.status_label.config(text="▶ Running", fg='#00ff00')
        else:
            messagebox.showerror("Error", result.get('message', 'Failed to resume session'))
    
    def stop_session(self):
        """Stop the current session"""
        if messagebox.askyesno("Stop Session", "Are you sure you want to stop the current session?"):
            result = self.app.stop_focus_session()
            if result['status'] == 'success':
                self.reset_ui()
            else:
                messagebox.showerror("Error", result.get('message', 'Failed to stop session'))
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ Pause", command=self.pause_session)
        self.stop_btn.config(state=tk.DISABLED)
        self.duration_spinbox.config(state=tk.NORMAL)
        self.status_label.config(text="⏸️ Not started", fg='#ffffff')
        self.timer_label.config(text="00:00")
        self.progress['value'] = 0
        self.task_label.config(text="")
        self.task_entry.config(state=tk.DISABLED)
        self.task_submit_btn.config(state=tk.DISABLED)
        self.webcam_status.config(text="📷 Webcam: Off", fg='#888888')
        self.screen_status.config(text="🖥️ Screen: Off", fg='#888888')
        self.user_status.config(text="👤 User: Unknown", fg='#888888')
    
    def submit_task(self):
        """Submit task verification"""
        user_input = self.task_entry.get()
        if user_input:
            result = self.app.verify_task(user_input)
            if result['status'] == 'success':
                self.task_label.config(text="✅ " + result['message'], fg='#00ff00')
                self.task_entry.delete(0, tk.END)
                self.task_entry.config(state=tk.DISABLED)
                self.task_submit_btn.config(state=tk.DISABLED)
            else:
                self.task_label.config(text="❌ " + result['message'], fg='#ff4444')
                self.task_entry.delete(0, tk.END)
    
    def update_status(self):
        """Update status information"""
        try:
            status = self.app.get_status()
            
            # Update timer
            focus_status = status.get('focus_status', {})
            remaining = focus_status.get('remaining_seconds', 0)
            minutes = remaining // 60
            seconds = remaining % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            
            # Update progress
            progress = focus_status.get('progress', 0) * 100
            self.progress['value'] = progress
            
            # Update webcam status
            webcam_status = status.get('webcam_status', {})
            if webcam_status.get('is_running', False):
                face_detected = webcam_status.get('face_detected', False)
                status_text = "✅ Face detected" if face_detected else "❌ No face"
                self.webcam_status.config(
                    text=f"📷 Webcam: {status_text}",
                    fg='#00ff00' if face_detected else '#ff4444'
                )
            
            # Update screen status
            screen_status = status.get('screen_status', {})
            if screen_status.get('is_running', False):
                entertainment = screen_status.get('entertainment_detected', False)
                status_text = "⚠️ Entertainment detected" if entertainment else "✅ Focused"
                self.screen_status.config(
                    text=f"🖥️ Screen: {status_text}",
                    fg='#ff4444' if entertainment else '#00ff00'
                )
            
            # Update user status
            user_present = status.get('user_present', True)
            if user_present:
                self.user_status.config(text="👤 User: Present", fg='#00ff00')
            else:
                self.user_status.config(text="👤 User: Away", fg='#ff4444')
            
            # Update task
            alert_status = status.get('alert_status', {})
            active_task = alert_status.get('active_task')
            if active_task:
                task_text = f"📝 Task: {active_task.get('task', {}).get('description', 'Unknown')}"
                self.task_label.config(text=task_text, fg='#ffd700')
                self.task_entry.config(state=tk.NORMAL)
                self.task_submit_btn.config(state=tk.NORMAL)
            else:
                # Only disable if no text is being entered
                if not self.task_entry.get():
                    self.task_entry.config(state=tk.DISABLED)
                    self.task_submit_btn.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Update error: {e}")
        
        # Schedule next update
        self.root.after(1000, self.update_status)
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application closed")

def main():
    """Main entry point for GUI"""
    app = FocusAppGUI()
    app.run()

if __name__ == "__main__":
    main()