# AI Chatbot (GPT-5-like)

A sophisticated Python-based AI chatbot inspired by ChatGPT with advanced GPT-5-like capabilities including:

- 🧠 **Advanced Reasoning**: Step-by-step problem solving and complex analysis
- 💭 **Long-term Memory**: Persistent conversation memory with semantic search
- 🛠️ **Tool Integration**: Web search, calculations, file operations, code execution
- 🎨 **Multimodal Support**: Text and image processing capabilities
- 🌐 **Multiple Interfaces**: Both CLI and web-based chat interfaces
- ⚡ **Multiple LLM Providers**: OpenAI, Anthropic, and local model support
- 🔧 **Extensible Architecture**: Easy to add new tools and capabilities

## Features

### Core AI Capabilities
- **Reasoning Engine**: Enhanced step-by-step reasoning for complex queries
- **Context Awareness**: Maintains conversation context across sessions
- **Memory Management**: Stores and retrieves relevant information from past conversations
- **Tool Use**: Automatically selects and uses appropriate tools based on user needs

### Supported Tools
- **Web Search**: Real-time information retrieval
- **Calculator**: Mathematical computations and equations
- **File Operations**: Read, write, and manage files
- **Code Execution**: Safe Python code execution environment
- **Weather**: Current weather information
- **DateTime**: Date and time queries

### Multiple LLM Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo support
- **Anthropic**: Claude models
- **Local Models**: HuggingFace Transformers integration

## Quick Start

### 1. Installation

```bash
# Clone and setup the project
git clone <repository-url>
cd ai-chatbot-gpt5
python setup.py
```

### 2. Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LLM_PROVIDER=openai
   LLM_MODEL=gpt-4o
   ```

### 3. Usage

#### CLI Interface
```bash
# Single message
python ui/cli/main.py chat -m "Explain quantum computing"

# Interactive session with custom session ID
python ui/cli/main.py chat -m "Hello" -s "my_session"

# List available tools
python ui/cli/main.py tools
```

#### Web Interface
```bash
# Start the web server
python ui/web/app.py

# Open browser to http://localhost:5000
```

## Project Structure

```
ai-chatbot-gpt5/
├── src/
│   ├── core/                 # Core chatbot functionality
│   │   ├── chatbot.py       # Main ChatBot class
│   │   └── conversation.py  # Conversation management
│   ├── ai/                  # AI components
│   │   ├── llm_client.py    # LLM provider clients
│   │   ├── memory_manager.py # Memory and context management
│   │   └── tool_manager.py  # Tool integration system
│   └── utils/               # Utility functions
├── ui/
│   ├── cli/                 # Command-line interface
│   │   └── main.py
│   └── web/                 # Web interface
│       ├── app.py          # Flask application
│       └── templates/      # HTML templates
├── config/                  # Configuration files
├── data/                    # Database and storage
├── docs/                    # Documentation
├── tests/                   # Test files
├── requirements.txt         # Python dependencies
├── setup.py                # Setup script
├── .env.example            # Environment template
└── README.md               # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `LLM_PROVIDER` | LLM provider (openai/anthropic/local) | openai |
| `LLM_MODEL` | Model name | gpt-4o |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `MAX_TOKENS` | Maximum response tokens | 4000 |
| `TEMPERATURE` | Response creativity (0.0-1.0) | 0.7 |
| `ENABLED_TOOLS` | Comma-separated list of tools | web_search,calculator,file_operations |
| `REASONING_ENABLED` | Enable step-by-step reasoning | true |
| `MEMORY_DB_PATH` | SQLite database path | data/memory.db |
| `VECTOR_DB_PATH` | ChromaDB path | data/chroma_db |

### Tool Configuration

Tools can be enabled/disabled by modifying the `ENABLED_TOOLS` environment variable:

```env
ENABLED_TOOLS=web_search,calculator,file_operations,weather,datetime,code_executor
```

## API Reference

### ChatBot Class

```python
from src.core.chatbot import ChatBot

# Initialize with configuration
config = {
    'llm': {'provider': 'openai', 'model': 'gpt-4o'},
    'memory': {'db_path': 'data/memory.db'},
    'tools': {'enabled_tools': ['web_search', 'calculator']}
}

bot = ChatBot(config)

# Process a message
response = await bot.process_message(
    "What's the weather like?", 
    context={'session_id': 'user123'}
)
```

### Memory Manager

```python
from src.ai.memory_manager import MemoryManager

memory = MemoryManager({'db_path': 'data/memory.db'})

# Store interaction
await memory.store_interaction(
    "What is Python?",
    "Python is a programming language..."
)

# Retrieve relevant memories
memories = await memory.retrieve_memories("programming languages")
```

### Tool Manager

```python
from src.ai.tool_manager import ToolManager

tools = ToolManager({'enabled_tools': ['calculator', 'web_search']})

# Analyze if tools are needed
needed = await tools.analyze_tool_need("What is 2+2?")

# Execute a tool
result = await tools.execute_tool('calculator', expression='2+2')
```

## Examples

### Basic Chat
```python
import asyncio
from src.core.chatbot import ChatBot

async def chat_example():
    config = {'llm': {'provider': 'openai', 'model': 'gpt-4o'}}
    bot = ChatBot(config)
    
    response = await bot.process_message("Hello, how are you?")
    print(response)

asyncio.run(chat_example())
```

### Using Tools
```python
# The chatbot automatically detects when tools are needed
response = await bot.process_message("What's 15% of 200?")
# Uses calculator tool automatically

response = await bot.process_message("Search for recent AI news")
# Uses web search tool automatically
```

### Memory and Context
```python
# First conversation
response1 = await bot.process_message(
    "My name is Alice", 
    context={'session_id': 'user1'}
)

# Later conversation - bot remembers
response2 = await bot.process_message(
    "What's my name?", 
    context={'session_id': 'user1'}
)
# Response: "Your name is Alice"
```

## Development

### Adding New Tools

1. Create a new tool function in `src/ai/tool_manager.py`:

```python
async def _my_custom_tool(self, param1: str, param2: int = 10) -> str:
    """My custom tool description."""
    # Tool implementation
    return f"Result: {param1} with {param2}"
```

2. Register the tool in `_register_builtin_tools()`:

```python
self.register_tool('my_tool', self._my_custom_tool, 
                  "My custom tool description")
```

3. Add pattern matching in `analyze_tool_need()` if needed.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Troubleshooting

### Common Issues

**"No module named 'src'" error:**
- Make sure you're running from the project root directory
- Check that `__init__.py` files exist in the src directories

**Memory database errors:**
- Ensure the `data/` directory exists
- Check file permissions for the database files

**API key errors:**
- Verify your API keys are correctly set in the `.env` file
- Check that the API key has sufficient credits/permissions

**Web interface not loading:**
- Check if port 5000 is available
- Try a different port by setting the `PORT` environment variable

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for their powerful language models
- Anthropic for Claude models
- The open-source community for the various libraries used

