# AI Agent System

A next-generation AI agent system built with LangGraph and LangSmith for enhanced observability, workflow control, and debugging capabilities.

## 🆕 LangGraph Agent (Recommended)

### ✨ Key Features

- **Graph-Based Workflow**: Uses LangGraph's StateGraph for flexible agent reasoning
- **LangSmith Integration**: Full observability with automatic tracing and debugging
- **Tool Integration**: Comprehensive set of tools for file, shell, web, and system operations
- **Memory Management**: Built-in conversation memory and state persistence
- **Error Handling**: Robust error handling with graceful recovery
- **Interactive Sessions**: Rich interactive CLI with history and commands
- **Async Support**: Full async/await support for better performance

### 🚀 Quick Start

1. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

2. **Set Environment Variables** (for LangSmith tracing and agent configuration):

```bash
# Optional (for LangSmith tracing)
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="your-langsmith-api-key"
export LANGSMITH_PROJECT="your-project-name"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"

# Optional (agent configuration)
export AGENT_MODEL="gpt-4o"
export AGENT_TEMPERATURE="0.1"
export AGENT_MAX_ITERATIONS="10"
```

3. **Run the LangGraph Agent**:

```bash
python -m langgraph_agent.main
```

### 🔧 LangGraph Agent Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Agent Node    │───▶│   Tool Node     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         │
                       ┌─────────────────┐              │
                       │ Should Continue?│◀─────────────┘
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Final Output  │
                       └─────────────────┘
```

### 🛠️ Available Tools

#### File Operations

- `read_file_tool` - Read file contents
- `write_file_tool` - Write content to files
- `edit_file_tool` - Search and replace in files
- `search_files_tool` - Search for files by pattern
- `list_directory_tool` - List directory contents
- `delete_file_tool` - Delete files and directories

#### Shell Commands

- `run_command_tool` - Execute shell commands
- `run_interactive_command_tool` - Start interactive processes
- `terminate_process_tool` - Terminate running processes
- `list_active_processes_tool` - List active processes

#### System Information

- `get_current_directory_tool` - Get current working directory
- `change_directory_tool` - Change working directory
- `get_system_info_tool` - Get detailed system information
- `get_environment_variable_tool` - Get environment variables
- `list_processes_tool` - List running processes
- `get_disk_usage_tool` - Get disk usage information

### 📊 LangSmith Integration (Experiment Tracking & Tracing)

The LangGraph agent includes built-in LangSmith integration for comprehensive observability:

#### Setup LangSmith

1. **Install LangSmith SDK** (included in requirements.txt):

```bash
pip install -U langsmith
```

2. **Set Environment Variables**:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-langsmith-api-key>
export LANGSMITH_PROJECT="My Project Name"
export LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
```

3. **Automatic Tracing**: The LangGraph agent automatically traces:

   - Agent reasoning steps
   - Tool executions
   - LLM calls with token usage
   - Error handling
   - Performance metrics

4. **View Traces**: Visit [LangSmith Dashboard](https://smith.langchain.com/) to view:
   - Detailed execution traces
   - Token usage analytics
   - Performance metrics
   - Error analysis
   - Conversation flows

### 💻 Usage Examples

#### Programmatic Usage

```python
import asyncio
from langgraph_agent import LangGraphAgent, LangGraphRunner

async def main():
    # Create agent
    agent = LangGraphAgent(
        model="gpt-4o",
        temperature=0.1,
        max_iterations=10
    )

    # Process a request
    response = await agent.process_request(
        user_input="List files in the current directory",
        user_id="user123",
        user_name="Alice"
    )

    print(response["response"])

asyncio.run(main())
```

#### Interactive Session

```python
from langgraph_agent import LangGraphRunner

async def interactive():
    runner = LangGraphRunner()
    await runner.run_interactive_session(
        user_name="Alice",
        working_directory="/path/to/project"
    )

asyncio.run(interactive())
```

### 📝 System Prompt Customization

The system prompt for the agent is stored in `langgraph_agent/prompt/system_prompt.txt`.

- To customize the agent's behavior or instructions, edit this file.
- If the file is missing, a minimal fallback prompt will be used.

### 📝 Development

#### Project Structure

```
├── langgraph_agent/           # LangGraph implementation
│   ├── core.py                # LangGraph agent
│   ├── runner.py              # Interactive runner
│   ├── state.py               # State management
│   ├── main.py                # Entry point
│   └── tools/                 # LangChain-compatible tools
│   ├── prompt/
│   │   └── system_prompt.txt  # System prompt for the agent (edit here to customize behavior)
├── requirements.txt           # Dependencies
```

#### Adding New Tools

1. Create a new tool file in `langgraph_agent/tools/`
2. Use the `@tool` decorator from `langchain_core.tools`
3. Add the tool to `ALL_TOOLS` in `langgraph_agent/tools/__init__.py`

Example:

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input_param: str) -> str:
    """
    Description of what the tool does.

    Args:
        input_param: Description of the parameter

    Returns:
        Description of the return value
    """
    # Tool implementation
    return f"Processed: {input_param}"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please:

1. Check the documentation above
2. Review the code examples
3. Open an issue on GitHub
4. Check LangSmith traces for debugging (LangGraph agent)

## 📧 Email Feature Setup (Gmail)

To enable the website generator to send generated site files via email, you must set the following environment variables with your Gmail credentials:

```bash
export GMAIL_USER="your-gmail-address@gmail.com"
export GMAIL_APP_PASSWORD="your-gmail-app-password"
```

- **GMAIL_USER**: Your Gmail address (e.g., myname@gmail.com)
- **GMAIL_APP_PASSWORD**: An [App Password](https://support.google.com/accounts/answer/185833) generated from your Google Account (not your regular Gmail password)

**Note:**

- You must enable 2-Step Verification on your Google account to generate an App Password.
- Never share your app password or commit it to version control.

The backend will use these credentials to send the generated website as a zip file to the user's email address.
