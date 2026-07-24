# gui/stats_page.py
"""Statistics page for the application"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from core.session_manager import SessionManager

class StatsPage:
    """Statistics display page"""
    
    def __init__(self, parent):
        self.parent = parent
        self.session_manager = SessionManager()
        self.setup_ui()
        self.load_stats()
    
    def setup_ui(self):
        """Setup the statistics UI"""
        # Main frame
        frame = ttk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(
            frame,
            text="📊 Statistics",
            font=('Arial', 20, 'bold'),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title.pack(pady=10)
        
        # Stats grid
        stats_frame = tk.Frame(frame, bg='#1a1a2e')
        stats_frame.pack(pady=20, fill=tk.X)
        
        # Create stat boxes
        self.stats = {}
        stat_names = [
            ('Total Focus Time', 'total_minutes', 'minutes'),
            ('Total Sessions', 'total_sessions', ''),
            ('Completed Sessions', 'completed_sessions', ''),
            ('Total Interruptions', 'total_interruptions', ''),
            ('Average Session', 'avg_minutes', 'minutes')
        ]
        
        for i, (label, key, unit) in enumerate(stat_names):
            box = tk.Frame(stats_frame, bg='#16213e', relief=tk.RAISED, bd=2)
            box.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5, pady=5)
            
            tk.Label(
                box,
                text=label,
                font=('Arial', 10),
                fg='#888888',
                bg='#16213e'
            ).pack(pady=(10, 0))
            
            value_label = tk.Label(
                box,
                text="0",
                font=('Arial', 20, 'bold'),
                fg='#00d4ff',
                bg='#16213e'
            )
            value_label.pack(pady=5)
            
            if unit:
                tk.Label(
                    box,
                    text=unit,
                    font=('Arial', 10),
                    fg='#888888',
                    bg='#16213e'
                ).pack(pady=(0, 10))
            
            self.stats[key] = value_label
        
        # Session history
        history_frame = tk.LabelFrame(frame, text="Recent Sessions", bg='#1a1a2e', fg='white')
        history_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview for sessions
        columns = ('Date', 'Duration', 'State', 'Interruptions')
        self.tree = ttk.Treeview(history_frame, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        refresh_btn = tk.Button(
            frame,
            text="🔄 Refresh",
            font=('Arial', 10),
            bg='#00d4ff',
            fg='#1a1a2e',
            command=self.load_stats
        )
        refresh_btn.pack(pady=10)
    
    def load_stats(self):
        """Load and display statistics"""
        try:
            # Load stats
            stats = self.session_manager.get_stats(30)
            
            # Update stat boxes
            for key, label in self.stats.items():
                value = stats.get(key, 0)
                if key in ['total_minutes', 'avg_minutes']:
                    value = round(value, 1)
                label.config(text=str(value))
            
            # Load session history
            sessions = self.session_manager.get_sessions(limit=10)
            self.tree.delete(*self.tree.get_children())
            
            for session in sessions:
                date = session.get('start_time', '')[:16] if session.get('start_time') else ''
                duration = session.get('duration_minutes', 0)
                state = session.get('state', 'unknown')
                interruptions = session.get('interruptions', 0)
                
                self.tree.insert('', 'end', values=(date, duration, state, interruptions))
                
        except Exception as e:
            print(f"Error loading stats: {e}")