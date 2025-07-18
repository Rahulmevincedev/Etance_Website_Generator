"""
LangGraph Agent System - A graph-based AI agent implementation
Built with LangGraph and LangSmith for enhanced observability and workflow control
"""

try:
    from .core import LangGraphAgent
    from .runner import LangGraphRunner
    from .state import AgentState
except ImportError as e:
    # Handle graceful import failure during development
    print(f"Warning: Import error in langgraph_agent package: {e}")
    LangGraphAgent = None
    LangGraphRunner = None
    AgentState = None

__version__ = "1.0.0"
__all__ = ["LangGraphAgent", "LangGraphRunner", "AgentState"] 