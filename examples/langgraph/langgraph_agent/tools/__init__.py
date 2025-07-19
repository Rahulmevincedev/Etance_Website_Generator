"""
LangChain-compatible tools for the LangGraph Agent System
Adapted from the original agent tools to work with LangChain's tool framework
"""

from .file_tools import (
    read_file_tool,
    write_file_tool,
    edit_file_tool,
    search_files_tool,
    list_directory_tool,
    delete_file_tool
)

from .shell_tools import (
    run_command_tool,
    run_interactive_command_tool,
    terminate_process_tool,
    list_active_processes_tool
)

from .web_tools import (
    web_search_tool,
    read_url_tool,
    download_file_tool
)

from .system_tools import (
    get_current_directory_tool,
    change_directory_tool,
    get_system_info_tool,
    get_environment_variable_tool,
    list_processes_tool,
    get_disk_usage_tool
)

# Export all tools
ALL_TOOLS = [
    # File tools
    read_file_tool,
    write_file_tool,
    edit_file_tool,
    search_files_tool,
    list_directory_tool,
    delete_file_tool,
    # Shell tools
    run_command_tool,
    run_interactive_command_tool,
    terminate_process_tool,
    list_active_processes_tool,
    # Web tools
    web_search_tool,
    read_url_tool,
    download_file_tool,
    # System tools
    get_current_directory_tool,
    change_directory_tool,
    get_system_info_tool,
    get_environment_variable_tool,
    list_processes_tool,
    get_disk_usage_tool
]

__all__ = [
    "ALL_TOOLS",
    "read_file_tool", "write_file_tool", "edit_file_tool", "search_files_tool",
    "list_directory_tool", "delete_file_tool", "run_command_tool",
    "run_interactive_command_tool", "terminate_process_tool", "list_active_processes_tool",
    "web_search_tool", "read_url_tool", "download_file_tool",
    "get_current_directory_tool", "change_directory_tool", "get_system_info_tool",
    "get_environment_variable_tool", "list_processes_tool", "get_disk_usage_tool"
] 