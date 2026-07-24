# src/main.py
"""Main entry point for the application"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )

def main():
    """Main function"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create application
        from app import FocusApplication
        app = FocusApplication()
        logger.info("Application started")
        
        print("\n" + "="*50)
        print("FOCUS MODE APPLICATION")
        print("="*50)
        print("\nCommands:")
        print("  start [minutes]  - Start focus session (default: 25 minutes)")
        print("  pause            - Pause current session")
        print("  resume           - Resume current session")
        print("  stop             - Stop current session")
        print("  status           - Show current status")
        print("  stats            - Show statistics")
        print("  task [input]     - Verify wake-up task")
        print("  quit/exit        - Exit application")
        print("="*50 + "\n")
        
        while True:
            try:
                command = input("> ").strip().lower()
                
                if not command:
                    continue
                    
                if command == "quit" or command == "exit":
                    if app.is_active:
                        app.stop_focus_session()
                    print("Goodbye!")
                    break
                    
                elif command.startswith("start"):
                    parts = command.split()
                    duration = int(parts[1]) if len(parts) > 1 else None
                    result = app.start_focus_session(duration)
                    print(f"Result: {result}")
                    
                elif command == "pause":
                    result = app.pause_focus_session()
                    print(f"Result: {result}")
                    
                elif command == "resume":
                    result = app.resume_focus_session()
                    print(f"Result: {result}")
                    
                elif command == "stop":
                    result = app.stop_focus_session()
                    print(f"Result: {result}")
                    
                elif command == "status":
                    status = app.get_status()
                    print("\nApplication Status:")
                    print("-" * 30)
                    print(f"Active: {status['is_active']}")
                    print(f"User Present: {status['user_present']}")
                    
                    focus_status = status.get('focus_status', {})
                    print(f"\nFocus Status:")
                    print(f"  State: {focus_status.get('state', 'unknown')}")
                    print(f"  Remaining: {focus_status.get('remaining_seconds', 0)} seconds")
                    print(f"  Progress: {focus_status.get('progress', 0) * 100:.1f}%")
                    
                    webcam_status = status.get('webcam_status', {})
                    print(f"\nWebcam Status:")
                    print(f"  Running: {webcam_status.get('is_running', False)}")
                    print(f"  Face Detected: {webcam_status.get('face_detected', False)}")
                    
                    screen_status = status.get('screen_status', {})
                    print(f"\nScreen Status:")
                    print(f"  Running: {screen_status.get('is_running', False)}")
                    print(f"  Entertainment Detected: {screen_status.get('entertainment_detected', False)}")
                    
                    alert_status = status.get('alert_status', {})
                    active_task = alert_status.get('active_task')
                    if active_task:
                        print(f"\nActive Task:")
                        print(f"  Task: {active_task.get('task', {}).get('description', 'Unknown')}")
                        print(f"  Remaining: {active_task.get('remaining_time', 0):.1f} seconds")
                    print("-" * 30 + "\n")
                    
                elif command == "stats":
                    stats = app.get_statistics()
                    if stats:
                        print("\nStatistics (Last 30 days):")
                        print("-" * 30)
                        print(f"Total Focus Minutes: {stats.get('total_minutes', 0)}")
                        print(f"Total Sessions: {stats.get('total_sessions', 0)}")
                        print(f"Completed Sessions: {stats.get('completed_sessions', 0)}")
                        print(f"Total Interruptions: {stats.get('total_interruptions', 0)}")
                        print(f"Average Session Duration: {stats.get('avg_minutes', 0):.1f} minutes")
                        print("-" * 30 + "\n")
                    else:
                        print("No statistics available yet\n")
                    
                elif command.startswith("task"):
                    parts = command.split(" ", 1)
                    if len(parts) > 1:
                        user_input = parts[1]
                        result = app.verify_task(user_input)
                        print(f"Task Verification: {result}")
                    else:
                        # Show active task
                        active_task = app.alert_system.get_active_task()
                        if active_task:
                            print(f"Active Task: {active_task.get('task', {}).get('description', 'Unknown')}")
                            print(f"Remaining Time: {active_task.get('remaining_time', 0):.1f} seconds")
                        else:
                            print("No active task")
                            
                else:
                    print(f"Unknown command: {command}")
                    print("Available commands: start, pause, resume, stop, status, stats, task [input], quit")
                    
            except KeyboardInterrupt:
                print("\nInterrupted")
                break
            except Exception as e:
                logger.error(f"Command error: {e}", exc_info=True)
                print(f"Error: {e}")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()