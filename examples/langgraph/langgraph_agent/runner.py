"""
LangGraph Agent Runner
Interactive session management for the LangGraph agent system
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .core import LangGraphAgent
from .state import create_initial_state

# Configure logging
logger = logging.getLogger(__name__)


class LangGraphRunner:
    """
    Runner for managing interactive sessions with the LangGraph agent.
    """
    
    def __init__(
        self,
        agent: Optional[LangGraphAgent] = None,
        model: str = "gpt-4o",
        temperature: float = 0.1,
        max_iterations: int = 10,
        enable_memory: bool = True
    ):
        """
        Initialize the LangGraph runner.
        
        Args:
            agent: Pre-configured LangGraph agent (optional)
            model: LLM model to use
            temperature: Model temperature
            max_iterations: Maximum iterations per conversation
            enable_memory: Whether to enable conversation memory
        """
        self.agent = agent or LangGraphAgent(
            model=model,
            temperature=temperature,
            max_iterations=max_iterations
        )
        self.enable_memory = enable_memory
        
        # Session management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        
        logger.info("LangGraph Runner initialized with memory support")
    
    async def run_interactive_session(
        self,
        user_id: str = "interactive_user",
        user_name: str = "User",
        working_directory: str = "."
    ) -> None:
        """
        Run an interactive session with the agent.
        
        Args:
            user_id: User identifier
            user_name: User's display name
            working_directory: Initial working directory
        """
        # Create session
        session_id = str(uuid.uuid4())
        thread_id = f"interactive_{session_id}"
        
        # Initialize session data
        session_data = {
            "session_id": session_id,
            "thread_id": thread_id,
            "user_id": user_id,
            "user_name": user_name,
            "working_directory": working_directory,
            "created_at": datetime.now().isoformat(),
            "interaction_count": 0
        }
        
        self.active_sessions[session_id] = session_data
        self.conversation_history[session_id] = []
        
        print(f"🤖 LangGraph Agent System - Interactive Session with Memory")
        print("=" * 60)
        print("Type 'quit', 'exit', or 'stop' to end the session")
        print("Type 'help' for available commands")
        print("Type 'history' to see conversation history")
        print("Type 'clear' to clear conversation history")
        print("Type 'info' to see agent information")
        print("=" * 60)
        print()
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input(f"🧑 {user_name}: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'stop']:
                        print("\n👋 Goodbye!")
                        break
                    
                    elif user_input.lower() == 'help':
                        self._show_help()
                        continue
                    
                    elif user_input.lower() == 'history':
                        self._show_history(session_id)
                        continue
                    
                    elif user_input.lower() == 'clear':
                        self._clear_history(session_id)
                        continue
                    
                    elif user_input.lower() == 'info':
                        self._show_agent_info()
                        continue
                    
                    # Process the request
                    print(f"\n🔄 Processing: {user_input}")
                    
                    response = await self.agent.process_request(
                        user_input=user_input,
                        user_id=user_id,
                        user_name=user_name,
                        working_directory=working_directory,
                        thread_id=thread_id
                    )
                    
                    # Display response
                    if response.get("success", False):
                        print(f"\n🤖 Agent: {response['response']}")
                        
                        # Update session data
                        session_data["interaction_count"] += 1
                        session_data["last_interaction"] = datetime.now().isoformat()
                        
                        # Store in conversation history
                        interaction = {
                            "timestamp": response.get("timestamp"),
                            "user_input": user_input,
                            "agent_response": response["response"],
                            "iteration_count": response.get("iteration_count", 0),
                            "tool_results": response.get("tool_results", []),
                            "success": True
                        }
                        self.conversation_history[session_id].append(interaction)
                        
                        # Show additional info if available
                        if response.get("iteration_count", 0) > 1:
                            print(f"   (Completed in {response['iteration_count']} iterations)")
                        
                        if response.get("tool_results"):
                            print(f"   (Used {len(response['tool_results'])} tool(s))")
                    
                    else:
                        print(f"\n❌ Error: {response.get('response', 'Unknown error')}")
                        
                        # Store error in history
                        interaction = {
                            "timestamp": response.get("timestamp"),
                            "user_input": user_input,
                            "agent_response": response.get("response", "Error occurred"),
                            "error": response.get("error"),
                            "success": False
                        }
                        self.conversation_history[session_id].append(interaction)
                    
                    print()  # Add spacing
                    
                except KeyboardInterrupt:
                    print("\n\n⚠️ Session interrupted by user")
                    break
                
                except Exception as e:
                    print(f"\n❌ Unexpected error: {str(e)}")
                    logger.error(f"Error in interactive session: {e}")
                    continue
        
        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Keep conversation history for potential review
            logger.info(f"Interactive session ended for {user_id}")
    
    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
🤖 LangGraph Agent System - Available Commands:

Interactive Commands:
  help     - Show this help message
  history  - Show conversation history
  clear    - Clear conversation history  
  info     - Show agent configuration
  quit     - Exit the session (also: exit, stop)

Agent Capabilities:
  📁 File Operations    - Read, write, edit, search files
  🖥️  Shell Commands     - Execute system commands safely
  🌐 Web Access        - Read URLs, download files
  📊 System Info       - Get system and process information
  🔧 General Tasks     - Code analysis, problem solving

Tips:
  - The agent has access to your file system and can execute commands
  - All operations include safety checks
  - Conversation history is maintained throughout the session
  - The agent can use multiple tools to complete complex tasks

Example requests:
  "List files in the current directory"
  "Read the contents of README.md"
  "Create a Python script that prints hello world"
  "Check system memory usage"
  "Search for Python files in this project"
"""
        print(help_text)
    
    def _show_history(self, session_id: str) -> None:
        """Show conversation history for a session."""
        if session_id not in self.conversation_history:
            print("No conversation history available.")
            return
        
        history = self.conversation_history[session_id]
        if not history:
            print("No conversation history available.")
            return
        
        print(f"\n📜 Conversation History ({len(history)} interactions):")
        print("-" * 50)
        
        for i, interaction in enumerate(history, 1):
            timestamp = interaction.get("timestamp", "Unknown")
            success_indicator = "✅" if interaction.get("success", False) else "❌"
            
            print(f"{i}. {timestamp} {success_indicator}")
            print(f"   🧑 User: {interaction['user_input']}")
            print(f"   🤖 Agent: {interaction['agent_response'][:100]}{'...' if len(interaction['agent_response']) > 100 else ''}")
            
            if interaction.get("tool_results"):
                print(f"   🔧 Tools used: {len(interaction['tool_results'])}")
            
            print()
    
    def _clear_history(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        if session_id in self.conversation_history:
            self.conversation_history[session_id] = []
            print("✅ Conversation history cleared.")
        else:
            print("No conversation history to clear.")
    
    def _show_agent_info(self) -> None:
        """Show agent configuration information."""
        info = self.agent.get_agent_info()
        
        print(f"\n🤖 Agent Configuration:")
        print(f"Model: {info['model']}")
        print(f"Temperature: {info['temperature']}")
        print(f"Max Iterations: {info['max_iterations']}")
        print(f"Available Tools: {info['num_tools']}")
        print(f"LangSmith Tracing: {'Enabled' if info['tracing_enabled'] else 'Disabled'}")
        print(f"System Prompt Length: {info['system_prompt_length']} characters")
        
        print(f"\n🔧 Available Tools:")
        for tool_name in info['tool_names']:
            print(f"  - {tool_name}")
        
        # Show session info if available
        if self.active_sessions:
            session_info = list(self.active_sessions.values())[0]
            print(f"\n📊 Current Session:")
            print(f"Session ID: {session_info['session_id']}")
            print(f"User: {session_info['user_name']}")
            print(f"Working Directory: {session_info['working_directory']}")
            print(f"Interactions: {session_info.get('interaction_count', 0)}")
    
    async def process_single_request(
        self,
        user_input: str,
        user_id: str = "default_user",
        user_name: str = "User",
        working_directory: str = ".",
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single request without interactive session.
        
        Args:
            user_input: User's input message
            user_id: User identifier
            user_name: User's display name
            working_directory: Current working directory
            session_id: Optional session ID for continuity
            
        Returns:
            Response dictionary
        """
        return await self.agent.process_request(
            user_input=user_input,
            user_id=user_id,
            user_name=user_name,
            working_directory=working_directory,
            session_id=session_id
        ) 