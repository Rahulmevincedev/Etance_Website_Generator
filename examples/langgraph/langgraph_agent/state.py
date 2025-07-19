"""
State management for LangGraph Agent System
Defines the state structure and management for graph-based agent workflows
"""

from typing import Dict, Any, List, Optional, TypedDict
from datetime import datetime
import uuid

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import Annotated


class UserContext(TypedDict):
    """User-specific context information"""
    user_id: str
    session_id: str
    name: str
    working_directory: str
    preferences: Dict[str, Any]
    permissions: Dict[str, bool]


class AgentState(TypedDict):
    """
    State for LangGraph agent that includes messages and additional context.
    Uses TypedDict for better type checking and LangGraph compatibility.
    """
    # Messages with proper reducer for LangGraph
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Additional state fields
    user_context: UserContext
    tool_results: List[Dict[str, Any]]
    session_info: Dict[str, Any]
    error_info: Optional[Dict[str, Any]]
    iteration_count: int


def create_initial_state(
    user_id: str = "default_user",
    session_id: Optional[str] = None,
    user_name: str = "User",
    working_directory: str = "."
) -> Dict[str, Any]:
    """Create initial state for a new conversation"""
    if not session_id:
        session_id = str(uuid.uuid4())
        
    return {
        "messages": [],
        "user_context": {
            "user_id": user_id,
            "session_id": session_id,
            "name": user_name,
            "working_directory": working_directory,
            "preferences": {
                "verbose_explanations": True,
                "step_by_step": True,
                "show_commands": True
            },
            "permissions": {
                "file_operations": True,
                "shell_commands": True,
                "web_access": True,
                "system_info": True
            }
        },
        "tool_results": [],
        "session_info": {
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "total_interactions": 0
        },
        "error_info": None,
        "iteration_count": 0
    }


def update_session_info(state: AgentState) -> Dict[str, Any]:
    """Update session information in state"""
    updated_session_info = state["session_info"].copy()
    updated_session_info["last_updated"] = datetime.now().isoformat()
    updated_session_info["total_interactions"] = updated_session_info.get("total_interactions", 0) + 1
    
    return {"session_info": updated_session_info}


def add_tool_result(state: AgentState, tool_name: str, result: Any, success: bool = True) -> Dict[str, Any]:
    """Add a tool execution result to the state"""
    tool_result = {
        "tool_name": tool_name,
        "result": result,
        "success": success,
        "timestamp": datetime.now().isoformat()
    }
    
    updated_tool_results = state["tool_results"].copy()
    updated_tool_results.append(tool_result)
    
    return {"tool_results": updated_tool_results}


def set_error(state: AgentState, error_message: str, error_type: str = "general") -> Dict[str, Any]:
    """Set error information in the state"""
    error_info = {
        "message": error_message,
        "type": error_type,
        "timestamp": datetime.now().isoformat()
    }
    
    return {"error_info": error_info}


def clear_error(state: AgentState) -> Dict[str, Any]:
    """Clear error information from the state"""
    return {"error_info": None}


def increment_iteration(state: AgentState) -> Dict[str, Any]:
    """Increment the iteration counter"""
    return {"iteration_count": state.get("iteration_count", 0) + 1}


# Type hints for better IDE support
AgentStateType = AgentState 