# gui/main_window_enhanced.py
"""Enhanced main window with tabs"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sys

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from gui.main_window import FocusAppGUI
from gui.settings_page import SettingsPage
from gui.stats_page import StatsPage

class EnhancedFocusAppGUI(FocusAppGUI):
    """Enhanced GUI with tabs for different views"""
    
    def __init__(self):
        super().__init__()
        self.root.title("Focus Mode Pro")
        self.root.geometry("900x700")
    
    def setup_ui(self):
        """Setup the enhanced UI with tabs"""
        # Create notebook (tab container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="🎯 Focus")
        
        # Stats tab
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="📊 Stats")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Settings")
        
        # Setup each tab
        self.setup_main_tab()
        self.setup_stats_tab()
        self.setup_settings_tab()
        
        # Configure styles
        self.configure_styles()
    
    def setup_main_tab(self):
        """Setup the main focus tab"""
        # Use the existing GUI setup but in the main tab
        # We need to override the parent frame
        original_main_frame = self.root
        self.root = self.main_tab
        
        # Call the original setup_ui
        super().setup_ui()
        
        # Restore root
        self.root = original_main_frame
        
        # Update status callback to use the main tab
        self.update_status = self._update_status_wrapper
        
    def setup_stats_tab(self):
        """Setup the statistics tab"""
        self.stats_page = StatsPage(self.stats_tab)
    
    def setup_settings_tab(self):
        """Setup the settings tab"""
        self.settings_page = SettingsPage(self.settings_tab)
    
    def configure_styles(self):
        """Configure custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 11))
    
    def _update_status_wrapper(self):
        """Wrapper for status update that doesn't interfere with tabs"""
        # Call the original update_status
        super().update_status()

def main():
    """Main entry point"""
    app = EnhancedFocusAppGUI()
    app.run()

if __name__ == "__main__":
    main()