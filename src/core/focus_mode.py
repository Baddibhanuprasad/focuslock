# src/core/focus_mode.py
"""Focus mode core logic with timer and state management"""

import time
import threading
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class FocusSession:
    """Focus session data model"""
    id: str
    duration_minutes: int
    start_time: datetime
    end_time: Optional[datetime] = None
    state: str = "idle"
    paused_time: Optional[datetime] = None
    paused_duration: int = 0
    interruptions: int = 0
    completed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects to strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

class FocusState(Enum):
    """Focus mode states"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"

class FocusMode:
    """Main focus mode controller"""
    
    def __init__(self):
        self.current_session: Optional[FocusSession] = None
        self.state = FocusState.IDLE
        self.remaining_seconds = 0
        self.timer_thread: Optional[threading.Thread] = None
        self.is_timer_running = False
        self.callbacks: Dict[str, list] = {
            'state_change': [],
            'time_update': [],
            'interruption': [],
            'completion': []
        }
        self._lock = threading.Lock()
    
    def start_session(self, duration_minutes: int) -> Dict[str, Any]:
        """Start a new focus session"""
        with self._lock:
            if self.state == FocusState.RUNNING:
                return {"status": "error", "message": "Session already running"}
            
            session_id = f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session = FocusSession(
                id=session_id,
                duration_minutes=duration_minutes,
                start_time=datetime.now(),
                state="running"
            )
            
            self.state = FocusState.RUNNING
            self.remaining_seconds = duration_minutes * 60
            self.is_timer_running = True
            
            # Start timer thread
            self.timer_thread = threading.Thread(target=self._timer_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
            self._trigger_callbacks('state_change', {
                'state': self.state.value,
                'session': self.current_session.to_dict()
            })
            
            return {
                "status": "success",
                "message": f"Focus session started for {duration_minutes} minutes",
                "session_id": session_id
            }
    
    def _timer_loop(self):
        """Main timer loop running in background"""
        while self.is_timer_running and self.remaining_seconds > 0:
            time.sleep(1)
            
            with self._lock:
                if self.state == FocusState.PAUSED:
                    continue
                    
                self.remaining_seconds -= 1
                
                # Calculate progress
                total_seconds = self.current_session.duration_minutes * 60
                progress = 1 - (self.remaining_seconds / total_seconds)
                
                self._trigger_callbacks('time_update', {
                    'remaining': self.remaining_seconds,
                    'progress': progress,
                    'elapsed': total_seconds - self.remaining_seconds,
                    'total': total_seconds
                })
                
                if self.remaining_seconds <= 0:
                    self._complete_session()
    
    def pause_session(self) -> Dict[str, Any]:
        """Pause the current session"""
        with self._lock:
            if self.state != FocusState.RUNNING:
                return {"status": "error", "message": "No running session to pause"}
            
            self.state = FocusState.PAUSED
            if self.current_session:
                self.current_session.paused_time = datetime.now()
                self.current_session.state = "paused"
            
            self._trigger_callbacks('state_change', {
                'state': self.state.value,
                'session': self.current_session.to_dict() if self.current_session else None
            })
            
            return {
                "status": "success",
                "message": "Focus session paused",
                "remaining": self.remaining_seconds
            }
    
    def resume_session(self) -> Dict[str, Any]:
        """Resume a paused session"""
        with self._lock:
            if self.state != FocusState.PAUSED:
                return {"status": "error", "message": "No paused session to resume"}
            
            if self.current_session and self.current_session.paused_time:
                # Calculate pause duration
                pause_duration = (datetime.now() - self.current_session.paused_time).seconds
                self.current_session.paused_duration += pause_duration
                self.current_session.paused_time = None
            
            self.state = FocusState.RUNNING
            if self.current_session:
                self.current_session.state = "running"
            
            self._trigger_callbacks('state_change', {
                'state': self.state.value,
                'session': self.current_session.to_dict() if self.current_session else None
            })
            
            return {
                "status": "success",
                "message": "Focus session resumed",
                "remaining": self.remaining_seconds
            }
    
    def _complete_session(self):
        """Complete the focus session"""
        with self._lock:
            self.state = FocusState.COMPLETED
            self.is_timer_running = False
            
            if self.current_session:
                self.current_session.end_time = datetime.now()
                self.current_session.completed = True
                self.current_session.state = "completed"
            
            self._trigger_callbacks('completion', {
                'session': self.current_session.to_dict() if self.current_session else None,
                'completed_at': datetime.now().isoformat()
            })
            
            self._trigger_callbacks('state_change', {
                'state': self.state.value,
                'session': self.current_session.to_dict() if self.current_session else None
            })
    
    def interrupt_session(self, reason: str) -> Dict[str, Any]:
        """Interrupt the session (e.g., due to distraction)"""
        with self._lock:
            if self.state != FocusState.RUNNING and self.state != FocusState.PAUSED:
                return {"status": "error", "message": "No active session to interrupt"}
            
            self.state = FocusState.INTERRUPTED
            self.is_timer_running = False
            
            if self.current_session:
                self.current_session.interruptions += 1
                self.current_session.state = "interrupted"
                self.current_session.end_time = datetime.now()
            
            self._trigger_callbacks('interruption', {
                'reason': reason,
                'session': self.current_session.to_dict() if self.current_session else None,
                'interrupted_at': datetime.now().isoformat()
            })
            
            self._trigger_callbacks('state_change', {
                'state': self.state.value,
                'session': self.current_session.to_dict() if self.current_session else None
            })
            
            return {
                "status": "success",
                "message": f"Session interrupted: {reason}",
                "session": self.current_session.to_dict() if self.current_session else None
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current session status"""
        with self._lock:
            status = {
                "state": self.state.value,
                "is_timer_running": self.is_timer_running,
                "remaining_seconds": self.remaining_seconds,
                "session": self.current_session.to_dict() if self.current_session else None
            }
            
            if self.current_session:
                total_seconds = self.current_session.duration_minutes * 60
                status["progress"] = 1 - (self.remaining_seconds / total_seconds) if total_seconds > 0 else 0
                status["elapsed_seconds"] = total_seconds - self.remaining_seconds
            
            return status
    
    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for specific events"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Trigger all callbacks for an event"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Callback error for {event_type}: {e}")