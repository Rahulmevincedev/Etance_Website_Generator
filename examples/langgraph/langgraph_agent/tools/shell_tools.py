"""
Shell command execution tools for the LangGraph Agent System
Adapted to use LangChain's @tool decorator for compatibility with LangGraph
"""

import subprocess
import os
import signal
import threading
import time
from typing import Dict, Any, Optional
from langchain_core.tools import tool

# Keep track of running processes for interactive commands
_running_processes: Dict[str, subprocess.Popen] = {}


@tool
def run_command_tool(command: str, timeout: int = 30, capture_output: bool = True, working_directory: str | None = None) -> str:
    """
    Execute a shell command and return the output.
    
    Args:
        command: Shell command to execute
        timeout: Timeout in seconds (default: 30)
        capture_output: Whether to capture stdout/stderr
        working_directory: Working directory for the command
        
    Returns:
        Command output and status information
    """
    try:
        # Safety checks - prevent dangerous commands
        dangerous_patterns = [
            'rm -rf /',
            'rm -rf *',
            'format',
            'fdisk',
            'mkfs',
            'dd if=',
            'chmod 777',
            'chown -R',
            '> /dev/sd',
            'shutdown',
            'reboot',
            'init 0',
            'init 6'
        ]
        
        command_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                return f"Error: Command blocked for safety reasons. Contains dangerous pattern: '{pattern}'"
        
        # Set working directory
        cwd = working_directory if working_directory else os.getcwd()
        
        # Execute command
        start_time = time.time()
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env=os.environ.copy()
        )
        
        execution_time = time.time() - start_time
        
        # Prepare output
        output_lines = []
        output_lines.append(f"Command: {command}")
        output_lines.append(f"Working Directory: {cwd}")
        output_lines.append(f"Exit Code: {result.returncode}")
        output_lines.append(f"Execution Time: {execution_time:.2f} seconds")
        output_lines.append("")
        
        if result.stdout:
            output_lines.append("STDOUT:")
            output_lines.append(result.stdout)
            output_lines.append("")
        
        if result.stderr:
            output_lines.append("STDERR:")
            output_lines.append(result.stderr)
            output_lines.append("")
        
        if result.returncode == 0:
            output_lines.append("✅ Command executed successfully")
        else:
            output_lines.append("❌ Command failed")
        
        return "\n".join(output_lines)
    
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after {timeout} seconds"
    except FileNotFoundError:
        return f"Error: Command not found: '{command}'"
    except PermissionError:
        return f"Error: Permission denied to execute command: '{command}'"
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"


@tool
def run_interactive_command_tool(command: str, process_id: str | None = None, input_data: str | None = None, timeout: int = 30) -> str:
    """
    Start or interact with an interactive command process.
    
    Args:
        command: Command to start (if process_id is None) or continue interacting with
        process_id: ID of existing process to interact with
        input_data: Input to send to the process
        timeout: Timeout for reading output
        
    Returns:
        Process output and status
    """
    try:
        if process_id is None:
            # Start new interactive process
            process_id = f"proc_{int(time.time())}"
            
            # Safety check
            if any(dangerous in command.lower() for dangerous in ['rm -rf', 'format', 'shutdown']):
                return f"Error: Interactive command blocked for safety: '{command}'"
            
            proc = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            _running_processes[process_id] = proc
            
            return f"Started interactive process '{command}' with ID: {process_id}\nUse this ID for further interactions."
        
        else:
            # Interact with existing process
            if process_id not in _running_processes:
                return f"Error: No active process with ID '{process_id}'"
            
            proc = _running_processes[process_id]
            
            # Check if process is still running
            if proc.poll() is not None:
                del _running_processes[process_id]
                return f"Process '{process_id}' has terminated with exit code: {proc.returncode}"
            
            # Send input if provided
            if input_data and proc.stdin:
                proc.stdin.write(input_data + "\n")
                proc.stdin.flush()
            
            # Read output with timeout
            output_lines = []
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Use select or polling to read without blocking indefinitely
                    if proc.stdout and proc.stdout.readable():
                        line = proc.stdout.readline()
                        if line:
                            output_lines.append(line.rstrip())
                        else:
                            break
                except:
                    break
                
                if time.time() - start_time > timeout:
                    break
            
            output = "\n".join(output_lines) if output_lines else "No output received"
            
            return f"Process ID: {process_id}\nInput sent: {input_data or 'None'}\n\nOutput:\n{output}"
    
    except Exception as e:
        return f"Error with interactive command: {str(e)}"


@tool
def terminate_process_tool(process_id: str) -> str:
    """
    Terminate a running interactive process.
    
    Args:
        process_id: ID of the process to terminate
        
    Returns:
        Termination status
    """
    try:
        if process_id not in _running_processes:
            return f"Error: No active process with ID '{process_id}'"
        
        proc = _running_processes[process_id]
        
        # Try graceful termination first
        proc.terminate()
        
        # Wait briefly for graceful shutdown
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # Force kill if graceful termination fails
            proc.kill()
            proc.wait()
        
        del _running_processes[process_id]
        
        return f"Successfully terminated process '{process_id}'"
    
    except Exception as e:
        return f"Error terminating process '{process_id}': {str(e)}"


@tool
def list_active_processes_tool() -> str:
    """
    List all active interactive processes.
    
    Returns:
        List of active processes
    """
    if not _running_processes:
        return "No active interactive processes"
    
    output_lines = ["Active interactive processes:"]
    
    for proc_id, proc in _running_processes.items():
        status = "Running" if proc.poll() is None else f"Terminated (exit code: {proc.returncode})"
        output_lines.append(f"  - {proc_id}: {status}")
    
    return "\n".join(output_lines) 