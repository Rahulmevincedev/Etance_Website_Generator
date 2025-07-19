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
# Add DeepSeek import
try:
    from langchain_deepseek import ChatDeepSeek
except ImportError:
    ChatDeepSeek = None  # Handle missing package gracefully
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState, create_initial_state
# Remove: from .tools import ALL_TOOLS
# Add MCP imports
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import json

# Configure logging
logger = logging.getLogger(__name__)


class LangGraphAgent:
    """
    LangGraph-based AI Agent with tool integration and LangSmith tracing.
    """
    
    def __init__(
        self,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_iterations: int = 10,
        tools: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        enable_tracing: bool = True
    ):
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.enable_tracing = enable_tracing
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        if tools is None:
            raise ValueError("Tools must be provided to __init__. Use LangGraphAgent.ainit for async tool loading.")
        self.tools = tools
        # Log loaded tool names
        logger.info(f"Loaded MCP tools: {[tool.name for tool in self.tools]}")
        # Dynamically append tool names and descriptions to system prompt
        tool_info = [
            f"{tool.name}: {getattr(tool, 'description', 'No description')}"
            for tool in self.tools
        ]
        tool_info_str = "\n".join(tool_info)
        self.system_prompt += (
            f"\n\nYou have access to the following MCP tools:\n{tool_info_str}\n"
            "When asked about your capabilities, list these tools and their descriptions."
        )
        # LLM selection logic
        if model.lower().startswith("deepseek"):
            if ChatDeepSeek is None:
                raise ImportError("langchain-deepseek is not installed. Please install it to use DeepSeek models.")
            self.llm = ChatDeepSeek(
                model=model,
                temperature=temperature
            )
            # Optionally bind tools if supported
            if hasattr(self.llm, 'bind_tools'):
                self.llm = self.llm.bind_tools(self.tools)
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature
            ).bind_tools(self.tools)
        self.graph = self._create_graph()
        logger.info(f"Initialized LangGraph Agent with model: {model}")
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent from a file."""
        prompt_path = os.path.join(os.path.dirname(__file__), 'prompt', 'system_prompt.txt')
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            # Fallback to a minimal prompt if file is missing or unreadable
            logger.warning(f"Could not load system prompt from {prompt_path}: {e}")
            return "You are an AI assistant. Use tools to help the user."

    async def _load_mcp_tools(self):
        # Load ONLY sequential thinking from MCP (reliable tool)
        # Load custom tools directly for file operations (more reliable)
        
        config_path = os.path.join(os.path.dirname(__file__), 'tools', 'mcp.json')
        
        # Load sequential thinking from MCP
        mcp_tools = []
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                mcp_config = json.load(f)
            
            # Only load sequential thinking MCP server
            sequential_thinking_config = {
                "sequential-thinking": mcp_config.get('mcpServers', {}).get('sequential-thinking')
            }
            
            if sequential_thinking_config["sequential-thinking"]:
                from langchain_mcp_adapters.client import MultiServerMCPClient
                client = MultiServerMCPClient(sequential_thinking_config)
                mcp_tools = await client.get_tools()
                logger.info(f"Loaded MCP sequential thinking tools: {[tool.name for tool in mcp_tools]}")
            else:
                logger.warning("Sequential thinking MCP server not found in config")
                
        except Exception as e:
            logger.error(f"Error loading MCP tools: {e}")
            # Continue with custom tools only if MCP fails
        
        # Load custom tools
        custom_tools = []
        try:
            from .tools import CUSTOM_TOOLS
            custom_tools = CUSTOM_TOOLS
            logger.info(f"Loaded custom tools: {[tool.name for tool in custom_tools]}")
        except Exception as e:
            logger.error(f"Error loading custom tools: {e}")
            
        # Combine MCP sequential thinking + custom tools  
        all_tools = mcp_tools + custom_tools
        
        if not all_tools:
            logger.warning("No tools loaded! Agent will not be able to perform actions.")
            
        return all_tools

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
            
            # Track tool call results for better error handling
            tool_results = []
            if hasattr(response, 'tool_calls') and response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_results.append({
                        'tool_name': tool_call.get('name', 'unknown'),
                        'attempted_at': datetime.now().isoformat(),
                        'tool_call_id': tool_call.get('id')
                    })
            
            return {
                "messages": [response],
                "iteration_count": new_iteration,
                "tool_results": tool_results
            }
            
        except Exception as e:
            logger.error(f"Error in agent node: {e}")
            error_message = AIMessage(
                content=f"""I encountered an error while processing your request: {str(e)}

**Troubleshooting Tips:**
1. If this is a file edit error, the issue might be with HTML formatting differences
2. Try being more specific about the content to change
3. Some edits may have succeeded partially - check the output files

Please try again or rephrase your request."""
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
            # Add recursion_limit to config
            config_dict = dict(config)
            config_dict["recursion_limit"] = 100
            
            # Create input state
            input_state = create_initial_state(
                user_id=user_id,
                session_id=session_id,
                user_name=user_name,
                working_directory=working_directory,
                available_tools=[tool.name for tool in self.tools]
            )
            input_state["messages"] = [HumanMessage(content=user_input)]
            
            # Run the graph with increased recursion limit
            result = await self.graph.ainvoke(input_state, config_dict)
            
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

    @classmethod
    async def ainit(
        cls,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_iterations: int = 10,
        tools: Optional[List[Any]] = None,
        system_prompt: Optional[str] = None,
        enable_tracing: bool = True
    ):
        self = cls.__new__(cls)
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.enable_tracing = enable_tracing
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        if tools is not None:
            self.tools = tools
        else:
            self.tools = await self._load_mcp_tools()
        # Log loaded tool names
        logger.info(f"Loaded MCP tools: {[tool.name for tool in self.tools]}")
        # Dynamically append tool names and descriptions to system prompt
        tool_info = [
            f"{tool.name}: {getattr(tool, 'description', 'No description')}"
            for tool in self.tools
        ]
        tool_info_str = "\n".join(tool_info)
        self.system_prompt += (
            f"\n\nYou have access to the following MCP tools:\n{tool_info_str}\n"
            "When asked about your capabilities, list these tools and their descriptions."
        )
        # LLM selection logic
        if model.lower().startswith("deepseek"):
            if ChatDeepSeek is None:
                raise ImportError("langchain-deepseek is not installed. Please install it to use DeepSeek models.")
            self.llm = ChatDeepSeek(
                model=model,
                temperature=temperature
            )
            if hasattr(self.llm, 'bind_tools'):
                self.llm = self.llm.bind_tools(self.tools)
        else:
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature
            ).bind_tools(self.tools)
        self.graph = self._create_graph()
        logger.info(f"Initialized LangGraph Agent with model: {model}")
        return self 