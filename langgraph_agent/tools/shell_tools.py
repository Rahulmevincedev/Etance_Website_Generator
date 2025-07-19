"""
Shell Tools for LangGraph Agent
Provides reliable shell command execution with timeout and error handling
"""

import subprocess
from typing import Dict, Any

from langchain_core.tools import tool


@tool  
def execute_shell_command(command: str, working_dir: str = ".") -> Dict[str, Any]:
    """
    Execute a shell command and return the result.
    
    Args:
        command: Command to execute
        working_dir: Working directory for command execution
        
    Returns:
        Dictionary with command results
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode,
            "command": command
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 30 seconds",
            "return_code": -1,
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "return_code": -1, 
            "command": command
        }


# Export shell tools
SHELL_TOOLS = [
    execute_shell_command
] 