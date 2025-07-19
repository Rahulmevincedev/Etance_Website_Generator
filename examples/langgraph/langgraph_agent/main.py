"""
Main entry point for the LangGraph Agent System
"""

import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

from .runner import LangGraphRunner
from .core import LangGraphAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the LangGraph agent system."""
    
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key in the .env file or environment variables")
        return
    
    # Check for LangSmith configuration (optional)
    langsmith_configured = all([
        os.getenv("LANGSMITH_TRACING"),
        os.getenv("LANGSMITH_API_KEY"),
        os.getenv("LANGSMITH_PROJECT")
    ])
    
    if langsmith_configured:
        print("✅ LangSmith tracing is configured")
    else:
        print("⚠️ LangSmith tracing is not fully configured (optional)")
        print("Set LANGSMITH_TRACING, LANGSMITH_API_KEY, and LANGSMITH_PROJECT for full observability")
    
    # Get configuration
    model = os.getenv("AGENT_MODEL", "gpt-4o")
    temperature = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
    max_iterations = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    
    print(f"🚀 Starting LangGraph Agent System...")
    print(f"Model: {model} | Temperature: {temperature} | Max Iterations: {max_iterations}")
    
    try:
        # Create agent
        agent = LangGraphAgent(
            model=model,
            temperature=temperature,
            max_iterations=max_iterations,
            enable_tracing=langsmith_configured
        )
        
        # Create runner
        runner = LangGraphRunner(agent=agent)
        
        # Get current working directory
        working_directory = str(Path.cwd())
        
        # Start interactive session
        await runner.run_interactive_session(
            user_id="interactive_user",
            user_name="User",
            working_directory=working_directory
        )
        
    except KeyboardInterrupt:
        print("\n👋 Session terminated by user")
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 