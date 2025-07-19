"""
Core LangGraph Agent Implementation
A graph-based AI agent with LangSmith tracing and tool integration
"""

import os
import logging
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState, create_initial_state
from .tools import ALL_TOOLS

# Configure logging
logger = logging.getLogger(__name__)


class LangGraphAgent:
    """
    LangGraph-based AI Agent with tool integration and LangSmith tracing.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.1,
        max_iterations: int = 10,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        enable_tracing: bool = True
    ):
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.enable_tracing = enable_tracing
        
        # Initialize tools
        self.tools = tools or ALL_TOOLS
        
        # Initialize LLM with tools
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature
        ).bind_tools(self.tools)
        
        # System prompt
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        
        # Create the graph
        self.graph = self._create_graph()
        
        logger.info(f"Initialized LangGraph Agent with model: {model}")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent."""
        return """You are an AI assistant powered by LangGraph and LangSmith. You help users with various tasks including:

- File operations (reading, writing, editing files)
- Shell command execution
- Web browsing and information retrieval
- System information and management
- Code analysis and development
- General problem-solving

You have access to a comprehensive set of tools. Use them appropriately to help the user accomplish their goals.

Key guidelines:
- Be helpful, accurate, and thorough
- Use tools when necessary to provide accurate information
- Explain your reasoning and steps clearly
- Handle errors gracefully and suggest alternatives
- Maintain user context and preferences
- Be proactive in suggesting useful next steps

Current capabilities:
- File system operations
- Shell command execution (with safety checks)
- Web content reading and downloading
- System information gathering
- Process management

Always prioritize user safety and data security when using tools."""

    def _create_graph(self):
        """Create the LangGraph workflow."""
        
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            },
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile with memory
        memory = MemorySaver()
        app = workflow.compile(checkpointer=memory)
        
        return app
    
    def _agent_node(self, state):
        """
        Agent reasoning node - processes messages and decides on actions.
        """
        try:
            # Get messages from state
            messages = state.get("messages", [])
            
            # Convert to list if needed
            if not isinstance(messages, list):
                messages = []
            
            # Add system message if this is the first interaction
            if not messages or not any(isinstance(msg, SystemMessage) for msg in messages):
                system_message = SystemMessage(content=self.system_prompt)
                messages = [system_message] + messages
            
            # Add user context to the conversation
            user_context = state.get("user_context", {})
            context_info = f"""
Current Context:
- Working Directory: {user_context.get('working_directory', 'Unknown')}
- User: {user_context.get('name', 'User')}
- Session: {user_context.get('session_id', 'Unknown')}
- Iteration: {state.get('iteration_count', 0)}
"""
            
            # Add context as a system message for this turn
            context_message = SystemMessage(content=context_info)
            messages_with_context = messages + [context_message]
            
            # Call LLM
            response = self.llm.invoke(messages_with_context)
            
            # Update iteration count
            new_iteration = state.get("iteration_count", 0) + 1
            
            return {
                "messages": [response],
                "iteration_count": new_iteration
            }
            
        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            error_message = AIMessage(
                content=f"I encountered an error while processing your request: {str(e)}. Please try again or rephrase your request."
            )
            return {
                "messages": [error_message],
                "error_info": {
                    "message": str(e),
                    "type": "agent_error",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _should_continue(self, state) -> Literal["continue", "end"]:
        """
        Determine whether to continue with tool calls or end the conversation.
        """
        # Get messages safely
        messages = state.get("messages", [])
        
        if not isinstance(messages, list) or not messages:
            return "end"
            
        last_message = messages[-1]
        
        # Check iteration limit
        iteration_count = state.get("iteration_count", 0)
        if iteration_count >= self.max_iterations:
            logger.warning(f"Reached maximum iterations ({self.max_iterations})")
            return "end"
        
        # If the last message has tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end the conversation
        return "end"
    
    async def process_request(
        self,
        user_input: str,
        user_id: str = "default_user",
        session_id: Optional[str] = None,
        user_name: str = "User",
        working_directory: str = ".",
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user request through the LangGraph workflow.
        
        Args:
            user_input: User's input message
            user_id: User identifier
            session_id: Session identifier
            user_name: User's display name
            working_directory: Current working directory
            thread_id: Thread ID for conversation continuity
            
        Returns:
            Response dictionary with agent output and metadata
        """
        try:
            # Create configuration
            thread_id = thread_id or session_id or f"thread_{user_id}"
            config = RunnableConfig(configurable={"thread_id": thread_id})
            
            # Create input state
            input_state = create_initial_state(
                user_id=user_id,
                session_id=session_id,
                user_name=user_name,
                working_directory=working_directory
            )
            input_state["messages"] = [HumanMessage(content=user_input)]
            
            # Run the graph
            result = await self.graph.ainvoke(input_state, config)
            
            # Extract the final response
            messages = result.get("messages", [])
            if not isinstance(messages, list):
                messages = []
            
            final_message = messages[-1] if messages else None
            
            if final_message and hasattr(final_message, 'content'):
                final_output = final_message.content
            else:
                final_output = "I apologize, but I couldn't generate a proper response."
            
            # Prepare response
            response = {
                "response": final_output,
                "success": True,
                "session_id": result.get("user_context", {}).get("session_id", session_id),
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.model,
                "iteration_count": result.get("iteration_count", 0),
                "tool_results": result.get("tool_results", []),
                "error_info": result.get("error_info"),
                "context": {
                    "working_directory": working_directory,
                    "user_name": user_name,
                    "thread_id": thread_id
                }
            }
            
            logger.info(f"Successfully processed request for {user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "response": f"I encountered an error while processing your request: {str(e)}",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "session_id": session_id
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the agent configuration."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "num_tools": len(self.tools),
            "tool_names": [tool.name for tool in self.tools],
            "tracing_enabled": self.enable_tracing,
            "system_prompt_length": len(self.system_prompt)
        } 