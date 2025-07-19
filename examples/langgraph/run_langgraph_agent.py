#!/usr/bin/env python3
"""
Entry script for the LangGraph Agent System
Run this to start the interactive LangGraph agent with LangSmith integration
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_agent.main import main

if __name__ == "__main__":
    print("🚀 Starting LangGraph Agent System...")
    print("📊 With LangSmith integration for enhanced observability")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Agent system terminated by user")
    except Exception as e:
        print(f"❌ Error starting agent system: {e}")
        sys.exit(1) 