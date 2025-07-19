"""
Directory Tools for LangGraph Agent
Provides reliable directory operations (copy, create, list)
"""

import shutil
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel


class FileEditResult(BaseModel):
    """Result of a file edit operation"""
    success: bool
    message: str
    changes_made: int = 0
    file_path: str = ""


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


# Export directory tools
DIRECTORY_TOOLS = [
    copy_directory,
    create_directory,
    list_directory_contents
] 