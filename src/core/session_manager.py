# src/core/session_manager.py
"""Session management and persistence"""

import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import hashlib

class SessionManager:
    """Manage focus sessions with persistence"""
    
    def __init__(self, db_path: str = "data/sessions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                duration_minutes INTEGER,
                start_time TEXT,
                end_time TEXT,
                state TEXT,
                paused_duration INTEGER DEFAULT 0,
                interruptions INTEGER DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                alert_type TEXT,
                message TEXT,
                details TEXT,
                timestamp TEXT,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Create statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                total_focus_minutes INTEGER DEFAULT 0,
                total_sessions INTEGER DEFAULT 0,
                completed_sessions INTEGER DEFAULT 0,
                interruptions INTEGER DEFAULT 0,
                avg_focus_minutes REAL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (id, duration_minutes, start_time, end_time, state, 
                 paused_duration, interruptions, completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_data.get('id'),
                session_data.get('duration_minutes'),
                session_data.get('start_time'),
                session_data.get('end_time'),
                session_data.get('state'),
                session_data.get('paused_duration', 0),
                session_data.get('interruptions', 0),
                1 if session_data.get('completed', False) else 0
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def get_sessions(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all sessions with pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM sessions 
                ORDER BY start_time DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def save_alert(self, alert_data: Dict[str, Any]) -> bool:
        """Save alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts (session_id, alert_type, message, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                alert_data.get('session_id'),
                alert_data.get('type'),
                alert_data.get('message'),
                json.dumps(alert_data.get('details', {})),
                alert_data.get('timestamp', datetime.now().isoformat())
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving alert: {e}")
            return False
    
    def get_alerts(self, session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get alerts, optionally filtered by session"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute("""
                    SELECT * FROM alerts 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor.execute("""
                    SELECT * FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting alerts: {e}")
            return []
    
    def update_stats(self) -> bool:
        """Update daily statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().date().isoformat()
            
            # Get today's sessions
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_sessions,
                    SUM(duration_minutes) as total_minutes,
                    SUM(interruptions) as total_interruptions
                FROM sessions 
                WHERE DATE(start_time) = ?
            """, (today,))
            
            row = cursor.fetchone()
            if row and row[0] > 0:
                total_sessions, completed, total_minutes, interruptions = row
                avg_minutes = total_minutes / total_sessions if total_sessions > 0 else 0
                
                cursor.execute("""
                    INSERT OR REPLACE INTO stats 
                    (date, total_focus_minutes, total_sessions, 
                     completed_sessions, interruptions, avg_focus_minutes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (today, total_minutes, total_sessions, completed, interruptions, avg_minutes))
                
                conn.commit()
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating stats: {e}")
            return False
    
    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get statistics for the last N days"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    SUM(total_focus_minutes) as total_minutes,
                    SUM(total_sessions) as total_sessions,
                    SUM(completed_sessions) as completed_sessions,
                    SUM(interruptions) as total_interruptions,
                    AVG(avg_focus_minutes) as avg_minutes
                FROM stats 
                WHERE date >= DATE('now', ?)
            """, (f'-{days} days',))
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else {}
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}