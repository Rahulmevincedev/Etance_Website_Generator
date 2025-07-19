"""
File operation tools for the LangGraph Agent System
Adapted to use LangChain's @tool decorator for compatibility with LangGraph
"""

import os
import glob
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from langchain_core.tools import tool


@tool
def read_file_tool(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File contents as string
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        
        if not path.is_file():
            return f"Error: '{file_path}' is not a file"
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"Successfully read file '{file_path}':\n\n{content}"
    
    except PermissionError:
        return f"Error: Permission denied to read file '{file_path}'"
    except UnicodeDecodeError:
        return f"Error: Unable to decode file '{file_path}' - may be a binary file"
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"


@tool
def write_file_tool(file_path: str, content: str, overwrite: bool = False) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        overwrite: Whether to overwrite existing file
        
    Returns:
        Success or error message
    """
    try:
        path = Path(file_path)
        
        # Check if file exists and overwrite is False
        if path.exists() and not overwrite:
            return f"Error: File '{file_path}' already exists. Use overwrite=True to replace it"
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote to file '{file_path}'"
    
    except PermissionError:
        return f"Error: Permission denied to write file '{file_path}'"
    except Exception as e:
        return f"Error writing file '{file_path}': {str(e)}"


@tool
def edit_file_tool(file_path: str, search_text: str, replace_text: str) -> str:
    """
    Edit a file by searching and replacing text.
    
    Args:
        file_path: Path to the file to edit
        search_text: Text to search for
        replace_text: Text to replace with
        
    Returns:
        Success or error message with details
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"
        
        # Read current content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if search text exists
        if search_text not in content:
            return f"Error: Search text not found in file '{file_path}'"
        
        # Perform replacement
        new_content = content.replace(search_text, replace_text)
        
        # Write back to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Count replacements
        replacements = content.count(search_text)
        
        return f"Successfully edited file '{file_path}': {replacements} occurrence(s) replaced"
    
    except PermissionError:
        return f"Error: Permission denied to edit file '{file_path}'"
    except Exception as e:
        return f"Error editing file '{file_path}': {str(e)}"


@tool
def search_files_tool(directory: str, pattern: str, file_extension: str = "*") -> str:
    """
    Search for files matching a pattern in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Pattern to search for (glob style)
        file_extension: File extension filter (default: all files)
        
    Returns:
        List of matching files
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not dir_path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        # Create search pattern
        if file_extension == "*":
            search_pattern = f"**/{pattern}"
        else:
            search_pattern = f"**/{pattern}.{file_extension.lstrip('.')}"
        
        # Search for files
        matches = []
        for file_path in dir_path.glob(search_pattern):
            if file_path.is_file():
                matches.append(str(file_path))
        
        if not matches:
            return f"No files found matching pattern '{pattern}' in directory '{directory}'"
        
        result = f"Found {len(matches)} file(s) matching pattern '{pattern}':\n"
        for match in sorted(matches):
            result += f"  - {match}\n"
        
        return result
    
    except Exception as e:
        return f"Error searching files: {str(e)}"


@tool
def list_directory_tool(directory: str, show_hidden: bool = False) -> str:
    """
    List contents of a directory.
    
    Args:
        directory: Directory to list
        show_hidden: Whether to show hidden files (starting with .)
        
    Returns:
        Directory listing with file details
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"Error: Directory '{directory}' does not exist"
        
        if not dir_path.is_dir():
            return f"Error: '{directory}' is not a directory"
        
        items = []
        for item in dir_path.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            item_info = {
                'name': item.name,
                'type': 'directory' if item.is_dir() else 'file',
                'size': item.stat().st_size if item.is_file() else 0,
                'modified': item.stat().st_mtime
            }
            items.append(item_info)
        
        # Sort by type (directories first) then by name
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        
        if not items:
            return f"Directory '{directory}' is empty"
        
        result = f"Contents of directory '{directory}':\n"
        for item in items:
            type_marker = "📁" if item['type'] == 'directory' else "📄"
            size_info = f" ({item['size']} bytes)" if item['type'] == 'file' else ""
            result += f"  {type_marker} {item['name']}{size_info}\n"
        
        return result
    
    except PermissionError:
        return f"Error: Permission denied to access directory '{directory}'"
    except Exception as e:
        return f"Error listing directory '{directory}': {str(e)}"


@tool
def delete_file_tool(file_path: str, confirm: bool = False) -> str:
    """
    Delete a file or directory.
    
    Args:
        file_path: Path to the file or directory to delete
        confirm: Confirmation flag to prevent accidental deletion
        
    Returns:
        Success or error message
    """
    try:
        if not confirm:
            return f"Error: Deletion requires confirmation. Set confirm=True to proceed with deleting '{file_path}'"
        
        path = Path(file_path)
        if not path.exists():
            return f"Error: Path '{file_path}' does not exist"
        
        if path.is_file():
            path.unlink()
            return f"Successfully deleted file '{file_path}'"
        elif path.is_dir():
            # For directories, only delete if empty for safety
            try:
                path.rmdir()
                return f"Successfully deleted empty directory '{file_path}'"
            except OSError:
                return f"Error: Directory '{file_path}' is not empty. Manual deletion required for safety"
        else:
            return f"Error: '{file_path}' is neither a file nor a directory"
    
    except PermissionError:
        return f"Error: Permission denied to delete '{file_path}'"
    except Exception as e:
        return f"Error deleting '{file_path}': {str(e)}" 