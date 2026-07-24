# src/alert/task_generator.py
"""Generate wake-up tasks"""

import random
from typing import Dict, Any

class TaskGenerator:
    """Generate and verify wake-up tasks"""
    
    def __init__(self):
        self.tasks = [
            {
                "id": "type_awake",
                "description": "Type the word 'AWAKE' five times",
                "verification": "text",
                "answer": "awake awake awake awake awake"
            },
            {
                "id": "space_bar",
                "description": "Press the space bar 10 times quickly",
                "verification": "action",
                "answer": None
            },
            {
                "id": "math_problem",
                "description": "Solve: 7 + 3 × 2 = ?",
                "verification": "text",
                "answer": "13"
            },
            {
                "id": "click_corners",
                "description": "Click on all four corners of the screen",
                "verification": "action",
                "answer": None
            },
            {
                "id": "reverse_name",
                "description": "Type your name backwards",
                "verification": "text",
                "answer": None  # Dynamic verification
            },
            {
                "id": "math_problem_2",
                "description": "What is 25 + 17? (type the answer)",
                "verification": "text",
                "answer": "42"
            }
        ]
        self.current_task = None
    
    def generate_task(self) -> Dict[str, Any]:
        """Generate a random task"""
        task = random.choice(self.tasks)
        self.current_task = task
        return task
    
    def verify_task(self, task: Dict[str, Any], user_input: str) -> Dict[str, Any]:
        """Verify task completion"""
        if not task:
            return {"status": "error", "message": "No task to verify"}
        
        verification_type = task.get("verification", "text")
        
        if verification_type == "text":
            if task.get("answer") and user_input.lower().strip() == task["answer"].lower():
                return {"status": "success", "message": "Task completed!"}
            elif not task.get("answer"):
                # For tasks without fixed answer (like reverse name)
                if len(user_input.strip()) > 0:
                    return {"status": "success", "message": "Task completed!"}
            return {"status": "failed", "message": "Incorrect input. Try again."}
        
        elif verification_type == "action":
            # For action-based tasks, assume success if any input is provided
            if user_input:
                return {"status": "success", "message": "Task completed!"}
            return {"status": "failed", "message": "Please perform the action"}
        
        return {"status": "failed", "message": "Unknown task type"}