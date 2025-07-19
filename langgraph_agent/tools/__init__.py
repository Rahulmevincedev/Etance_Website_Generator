"""
Enhanced tools package using LangChain's official FileManagementToolkit
and custom HTML tools with BeautifulSoup for surgical editing.
"""

from langchain_community.agent_toolkits import FileManagementToolkit
from .html_tools import HTML_TOOLS
from .shell_tools import SHELL_TOOLS
from pathlib import Path
import os

# Initialize the official FileManagementToolkit
# Restrict to project root for security
project_root = Path(__file__).parent.parent.parent  # Go up to Etance_Website_Generator
toolkit = FileManagementToolkit(
    root_dir=str(project_root),
    selected_tools=["read_file", "write_file", "list_directory", "copy_file", "move_file"]
)
file_management_tools = toolkit.get_tools()

# Combine all reliable tools for the agent
# Official toolkit for basics + custom HTML tools + shell tools
ALL_TOOLS = file_management_tools + HTML_TOOLS + SHELL_TOOLS

# Export for easy import
CUSTOM_TOOLS = ALL_TOOLS

# Export individual modules for direct access if needed
__all__ = [
    'CUSTOM_TOOLS',
    'FILE_TOOLS',
    'DIRECTORY_TOOLS', 
    'SHELL_TOOLS'
] 