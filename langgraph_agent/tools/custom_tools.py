"""
Custom LangGraph Tools for Reliable File Editing
This module provides robust file editing tools that handle HTML content properly,
replacing the unreliable desktop-commander edit_block tool.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from difflib import SequenceMatcher

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FileEditResult(BaseModel):
    """Result of a file edit operation"""
    success: bool
    message: str
    changes_made: int = 0
    file_path: str = ""


def normalize_line_endings(text: str) -> str:
    """Normalize line endings to LF only"""
    return text.replace('\r\n', '\n').replace('\r', '\n')


def similarity_score(a: str, b: str) -> float:
    """Calculate similarity score between two strings"""
    return SequenceMatcher(None, a, b).ratio()


@tool
def read_file_content(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Read the contents of a file with optional line range.
    
    Args:
        file_path: Path to the file to read
        start_line: Starting line number (1-based, optional)  
        end_line: Ending line number (1-based, optional)
        
    Returns:
        File content as string
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        if start_line is not None or end_line is not None:
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            lines = lines[start_idx:end_idx]
            
        content = ''.join(lines)
        return normalize_line_endings(content)
        
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool
def write_file_content(file_path: str, content: str, create_dirs: bool = True) -> FileEditResult:
    """
    Write content to a file, creating directories if needed.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories
        
    Returns:
        FileEditResult with operation status
    """
    try:
        file_path = Path(file_path)
        
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
        # Normalize line endings
        normalized_content = normalize_line_endings(content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(normalized_content)
            
        return FileEditResult(
            success=True,
            message=f"Successfully wrote to {file_path}",
            changes_made=1,
            file_path=str(file_path)
        )
        
    except Exception as e:
        return FileEditResult(
            success=False,
            message=f"Error writing file: {str(e)}",
            file_path=str(file_path)
        )


@tool 
def smart_text_replace(
    file_path: str,
    old_text: str, 
    new_text: str,
    max_replacements: Optional[int] = None,
    case_sensitive: bool = True,
    fuzzy_threshold: float = 0.85
) -> FileEditResult:
    """
    Replace text in a file with smart matching for HTML content.
    Handles line ending differences and provides fuzzy matching.
    
    Args:
        file_path: Path to the file to edit
        old_text: Text to find and replace
        new_text: Text to replace with  
        max_replacements: Maximum number of replacements (None for all)
        case_sensitive: Whether search should be case sensitive
        fuzzy_threshold: Minimum similarity for fuzzy matching (0.0-1.0)
        
    Returns:
        FileEditResult with operation details
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Normalize line endings for both content and search text
        content_normalized = normalize_line_endings(content)
        old_text_normalized = normalize_line_endings(old_text)
        new_text_normalized = normalize_line_endings(new_text)
        
        changes_made = 0
        
        # Try exact match first
        if case_sensitive:
            if old_text_normalized in content_normalized:
                if max_replacements:
                    # Count existing occurrences
                    count = content_normalized.count(old_text_normalized)
                    if count > max_replacements:
                        # Replace only the specified number
                        content_normalized = content_normalized.replace(old_text_normalized, new_text_normalized, max_replacements)
                        changes_made = max_replacements
                    else:
                        content_normalized = content_normalized.replace(old_text_normalized, new_text_normalized)
                        changes_made = count
                else:
                    content_normalized = content_normalized.replace(old_text_normalized, new_text_normalized)
                    changes_made = content_normalized.count(new_text_normalized) if old_text_normalized != new_text_normalized else 1
        else:
            # Case insensitive replacement
            pattern = re.escape(old_text_normalized)
            matches = list(re.finditer(pattern, content_normalized, re.IGNORECASE))
            
            if max_replacements:
                matches = matches[:max_replacements]
                
            # Replace from end to beginning to maintain positions
            for match in reversed(matches):
                content_normalized = (content_normalized[:match.start()] + 
                                    new_text_normalized + 
                                    content_normalized[match.end():])
                changes_made += 1
        
        # If exact match failed, try fuzzy matching for HTML content
        if changes_made == 0 and fuzzy_threshold > 0:
            lines = content_normalized.split('\n')
            old_lines = old_text_normalized.split('\n')
            
            # Look for fuzzy matches in sliding windows
            for i in range(len(lines) - len(old_lines) + 1):
                window = '\n'.join(lines[i:i + len(old_lines)])
                similarity = similarity_score(window, old_text_normalized)
                
                if similarity >= fuzzy_threshold:
                    # Replace the fuzzy match
                    lines[i:i + len(old_lines)] = new_text_normalized.split('\n')
                    content_normalized = '\n'.join(lines)
                    changes_made = 1
                    break
        
        # Write back if changes were made
        if changes_made > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content_normalized)
                
            return FileEditResult(
                success=True,
                message=f"Successfully replaced {changes_made} occurrence(s) in {file_path}",
                changes_made=changes_made,
                file_path=file_path
            )
        else:
            return FileEditResult(
                success=False,
                message=f"Text not found in {file_path}. Try using more specific context or check for formatting differences.",
                changes_made=0,
                file_path=file_path
            )
            
    except Exception as e:
        return FileEditResult(
            success=False,
            message=f"Error editing file: {str(e)}",
            file_path=file_path
        )


@tool
def copy_directory(source_path: str, dest_path: str, overwrite: bool = True) -> FileEditResult:
    """
    Copy a directory and all its contents to a new location.
    
    Args:
        source_path: Source directory path
        dest_path: Destination directory path  
        overwrite: Whether to overwrite existing destination
        
    Returns:
        FileEditResult with operation status
    """
    try:
        source = Path(source_path)
        dest = Path(dest_path)
        
        if not source.exists():
            return FileEditResult(
                success=False,
                message=f"Source directory {source_path} does not exist",
                file_path=dest_path
            )
            
        if dest.exists() and not overwrite:
            return FileEditResult(
                success=False, 
                message=f"Destination {dest_path} already exists and overwrite=False",
                file_path=dest_path
            )
            
        if dest.exists() and overwrite:
            shutil.rmtree(dest)
            
        shutil.copytree(source, dest)
        
        # Count copied files
        file_count = sum(1 for _ in dest.rglob('*') if _.is_file())
        
        return FileEditResult(
            success=True,
            message=f"Successfully copied {file_count} files from {source_path} to {dest_path}",
            changes_made=file_count,
            file_path=dest_path
        )
        
    except Exception as e:
        return FileEditResult(
            success=False,
            message=f"Error copying directory: {str(e)}",
            file_path=dest_path
        )


@tool
def create_directory(dir_path: str) -> FileEditResult:
    """
    Create a directory and any necessary parent directories.
    
    Args:
        dir_path: Directory path to create
        
    Returns:
        FileEditResult with operation status  
    """
    try:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        return FileEditResult(
            success=True,
            message=f"Successfully created directory {dir_path}",
            changes_made=1,
            file_path=dir_path
        )
        
    except Exception as e:
        return FileEditResult(
            success=False,
            message=f"Error creating directory: {str(e)}",
            file_path=dir_path
        )


@tool
def list_directory_contents(dir_path: str, show_hidden: bool = False) -> str:
    """
    List the contents of a directory.
    
    Args:
        dir_path: Directory path to list
        show_hidden: Whether to show hidden files
        
    Returns:
        Directory listing as formatted string
    """
    try:
        path = Path(dir_path)
        if not path.exists():
            return f"Directory {dir_path} does not exist"
            
        items = []
        for item in path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
                
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            size = ""
            if item.is_file():
                size = f" ({item.stat().st_size} bytes)"
            items.append(f"{item_type} {item.name}{size}")
            
        return "\n".join(sorted(items)) if items else "Directory is empty"
        
    except Exception as e:
        return f"Error listing directory: {str(e)}"


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


# Export all tools for easy import
CUSTOM_TOOLS = [
    read_file_content,
    write_file_content,
    smart_text_replace,
    copy_directory,
    create_directory,
    list_directory_contents,
    execute_shell_command
] 