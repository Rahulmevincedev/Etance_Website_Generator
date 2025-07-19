"""
System utility tools for the LangGraph Agent System
Adapted to use LangChain's @tool decorator for compatibility with LangGraph
"""

import os
import platform
import psutil
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool


@tool
def get_current_directory_tool() -> str:
    """
    Get the current working directory.
    
    Returns:
        Current working directory path
    """
    try:
        current_dir = os.getcwd()
        return f"Current working directory: {current_dir}"
    except Exception as e:
        return f"Error getting current directory: {str(e)}"


@tool
def change_directory_tool(directory: str) -> str:
    """
    Change the current working directory.
    
    Args:
        directory: Directory to change to
        
    Returns:
        Success or error message
    """
    try:
        path = Path(directory)
        if not path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        os.chdir(directory)
        new_dir = os.getcwd()
        return f"Successfully changed directory to: {new_dir}"
    
    except PermissionError:
        return f"Error: Permission denied to access directory '{directory}'"
    except Exception as e:
        return f"Error changing directory to '{directory}': {str(e)}"


@tool
def get_system_info_tool() -> str:
    """
    Get system information.
    
    Returns:
        Detailed system information
    """
    try:
        info_lines = []
        
        # Basic system info
        info_lines.append("=== SYSTEM INFORMATION ===")
        info_lines.append(f"Platform: {platform.platform()}")
        info_lines.append(f"System: {platform.system()}")
        info_lines.append(f"Release: {platform.release()}")
        info_lines.append(f"Version: {platform.version()}")
        info_lines.append(f"Machine: {platform.machine()}")
        info_lines.append(f"Processor: {platform.processor()}")
        info_lines.append("")
        
        # Python info
        info_lines.append("=== PYTHON INFORMATION ===")
        info_lines.append(f"Python Version: {platform.python_version()}")
        info_lines.append(f"Python Implementation: {platform.python_implementation()}")
        info_lines.append("")
        
        # CPU info
        if hasattr(psutil, 'cpu_count'):
            info_lines.append("=== CPU INFORMATION ===")
            info_lines.append(f"CPU Cores (Physical): {psutil.cpu_count(logical=False)}")
            info_lines.append(f"CPU Cores (Logical): {psutil.cpu_count(logical=True)}")
            info_lines.append(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
            info_lines.append("")
        
        # Memory info
        if hasattr(psutil, 'virtual_memory'):
            memory = psutil.virtual_memory()
            info_lines.append("=== MEMORY INFORMATION ===")
            info_lines.append(f"Total Memory: {memory.total / (1024**3):.2f} GB")
            info_lines.append(f"Available Memory: {memory.available / (1024**3):.2f} GB")
            info_lines.append(f"Used Memory: {memory.used / (1024**3):.2f} GB")
            info_lines.append(f"Memory Usage: {memory.percent}%")
            info_lines.append("")
        
        # Disk info
        if hasattr(psutil, 'disk_usage'):
            disk = psutil.disk_usage('/')
            info_lines.append("=== DISK INFORMATION ===")
            info_lines.append(f"Total Disk Space: {disk.total / (1024**3):.2f} GB")
            info_lines.append(f"Used Disk Space: {disk.used / (1024**3):.2f} GB")
            info_lines.append(f"Free Disk Space: {disk.free / (1024**3):.2f} GB")
            info_lines.append(f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%")
            info_lines.append("")
        
        # Working directory
        info_lines.append("=== WORKING DIRECTORY ===")
        info_lines.append(f"Current Directory: {os.getcwd()}")
        info_lines.append("")
        
        # Environment variables (selected)
        info_lines.append("=== KEY ENVIRONMENT VARIABLES ===")
        key_env_vars = ['PATH', 'HOME', 'USER', 'SHELL', 'PYTHON_PATH']
        for var in key_env_vars:
            value = os.environ.get(var, 'Not set')
            if var == 'PATH':
                # Truncate PATH for readability
                if len(value) > 200:
                    value = value[:200] + '... [truncated]'
            info_lines.append(f"{var}: {value}")
        
        return "\n".join(info_lines)
    
    except ImportError:
        return "System information partially available (psutil not installed)\n" + \
               f"Platform: {platform.platform()}\n" + \
               f"Python: {platform.python_version()}\n" + \
               f"Current Directory: {os.getcwd()}"
    except Exception as e:
        return f"Error getting system information: {str(e)}"


@tool
def get_environment_variable_tool(variable_name: str) -> str:
    """
    Get the value of an environment variable.
    
    Args:
        variable_name: Name of the environment variable
        
    Returns:
        Environment variable value or error message
    """
    try:
        value = os.environ.get(variable_name)
        if value is None:
            return f"Environment variable '{variable_name}' is not set"
        return f"{variable_name}={value}"
    except Exception as e:
        return f"Error getting environment variable '{variable_name}': {str(e)}"


@tool
def list_processes_tool(limit: int = 10) -> str:
    """
    List running processes (limited for security).
    
    Args:
        limit: Maximum number of processes to show
        
    Returns:
        List of running processes
    """
    try:
        if not hasattr(psutil, 'process_iter'):
            return "Process listing not available (psutil not installed or insufficient permissions)"
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        # Limit results
        processes = processes[:limit]
        
        if not processes:
            return "No process information available"
        
        result_lines = [f"Top {limit} processes by CPU usage:"]
        result_lines.append(f"{'PID':<8} {'Name':<20} {'CPU%':<8} {'Memory%'}")
        result_lines.append("-" * 50)
        
        for proc in processes:
            pid = proc.get('pid', 'N/A')
            name = proc.get('name', 'N/A')[:20]  # Truncate long names
            cpu = f"{proc.get('cpu_percent', 0):.1f}%"
            memory = f"{proc.get('memory_percent', 0):.1f}%"
            result_lines.append(f"{pid:<8} {name:<20} {cpu:<8} {memory}")
        
        return "\n".join(result_lines)
    
    except Exception as e:
        return f"Error listing processes: {str(e)}"


@tool
def get_disk_usage_tool(path: str = ".") -> str:
    """
    Get disk usage information for a specific path.
    
    Args:
        path: Path to check disk usage for
        
    Returns:
        Disk usage information
    """
    try:
        if not hasattr(psutil, 'disk_usage'):
            return f"Disk usage information not available for '{path}'"
        
        usage = psutil.disk_usage(path)
        
        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        usage_percent = (usage.used / usage.total) * 100
        
        result_lines = [
            f"Disk usage for path: {path}",
            f"Total: {total_gb:.2f} GB",
            f"Used: {used_gb:.2f} GB ({usage_percent:.1f}%)",
            f"Free: {free_gb:.2f} GB"
        ]
        
        return "\n".join(result_lines)
    
    except FileNotFoundError:
        return f"Error: Path '{path}' not found"
    except Exception as e:
        return f"Error getting disk usage for '{path}': {str(e)}" 