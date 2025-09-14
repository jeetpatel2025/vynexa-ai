# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Development Commands

### Initial Setup
```bash
# Set up the project with dependencies and virtual environment
python setup.py

# Copy environment template (if not already exists)
cp .env.example .env
# Then edit .env with your API keys

# Manual dependency installation if needed
pip install -r requirements.txt
```

### Running the Application

**CLI Interface:**
```bash
# Single message interaction
python ui/cli/main.py chat -m "Your message here"

# Interactive session with session ID
python ui/cli/main.py chat -m "Hello" -s "session_name"

# List available tools
python ui/cli/main.py tools
```

**Web Interface:**
```bash
# Start web server (default: http://localhost:5000)
python ui/web/app.py
```

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (when test directory exists)
pytest tests/ -v
```

### Development Tasks
```bash
# Check configuration validity
python -c "from config.config import config; print('Valid' if config.validate() else 'Invalid')"

# Create necessary directories
python -c "from config.config import config; config.create_directories()"
```

## Architecture Overview

This is a sophisticated AI chatbot with GPT-5-like capabilities built on a modular architecture:

### Core Components

**`src/core/chatbot.py`** - Main orchestrator that coordinates all AI functionality:
- Manages conversation flow and context
- Integrates LLM client, memory manager, and tool manager
- Handles step-by-step reasoning when enabled
- Entry point for all user interactions

**`src/ai/llm_client.py`** - Unified LLM provider interface:
- Supports multiple providers: OpenAI, Anthropic, and local models
- Handles multimodal capabilities (text + image)
- Manages API rate limits and error handling

**`src/ai/memory_manager.py`** - Long-term memory system:
- Uses SQLite for structured storage and ChromaDB for vector embeddings
- Implements semantic search for conversation history
- Stores user preferences and session context
- Enables context-aware responses across sessions

**`src/ai/tool_manager.py`** - Function calling and external integrations:
- Pattern-based tool need analysis
- Built-in tools: web search, calculator, file operations, weather, datetime, code executor
- Extensible system for custom tool registration
- Safe execution environment with basic security checks

### Data Flow Architecture

1. **User Input** → `ChatBot.process_message()`
2. **Memory Retrieval** → Semantic search for relevant past conversations
3. **Tool Analysis** → Pattern matching to determine needed tools
4. **LLM Generation** → Context-aware response with reasoning
5. **Memory Storage** → Store interaction for future reference

### Configuration System

The `config/config.py` module provides centralized configuration management:
- Environment variable loading with defaults
- Validation of required API keys based on LLM provider
- Directory creation for data/logs/models
- Support for multiple LLM providers with different configurations

### Tool System Design

Tools are registered functions with automatic pattern-based triggering:
- **Analysis Phase**: `analyze_tool_need()` uses regex patterns to identify needed tools
- **Execution Phase**: `execute_tool()` safely executes with error handling
- **Extension**: New tools added by registering functions with descriptions

## Environment Configuration

Required environment variables based on LLM provider:

**OpenAI (default):**
- `LLM_PROVIDER=openai`
- `LLM_MODEL=gpt-4o`
- `OPENAI_API_KEY=sk-...`

**Anthropic:**
- `LLM_PROVIDER=anthropic`
- `ANTHROPIC_API_KEY=sk-ant-...`

**Tool Configuration:**
- `ENABLED_TOOLS=web_search,calculator,file_operations,weather,datetime`
- `REASONING_ENABLED=true`

**Optional external API keys:**
- `OPENWEATHER_API_KEY` for weather tool
- `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_ENGINE_ID` for web search

## Key Development Patterns

### Adding New Tools
1. Create async function in `ToolManager` with proper type hints
2. Register tool in `_register_builtin_tools()` with description
3. Add pattern matching in `analyze_tool_need()` if needed
4. Follow security best practices for external API calls

### Extending LLM Support
- Add new provider in `LLMClient` with unified interface
- Update configuration validation in `Config.validate()`
- Maintain consistent message format across providers

### Memory Management
- All interactions automatically stored with semantic embeddings
- Use session IDs for conversation continuity
- Memory retrieval based on similarity thresholds
- Consider cleanup for production deployments

## Project Structure Notes

```
src/
├── core/          # Main chatbot logic and conversation management
├── ai/            # AI-specific components (LLM, memory, tools)
└── utils/         # Shared utilities

ui/
├── cli/           # Command-line interface
└── web/           # Flask web interface with templates

config/            # Centralized configuration management
data/              # SQLite database and ChromaDB storage
docs/              # API documentation and guides
```

## Development Considerations

- **Async/Await**: All core functions are async for better performance
- **Error Handling**: Each component has specific error handling patterns
- **Security**: File operations and code execution have safety restrictions
- **Memory**: Vector database can grow large - implement cleanup strategies
- **API Limits**: Respect rate limits for external services
- **Sessions**: Support for multiple concurrent user sessions

## Tool Safety Notes

The built-in tools have basic security measures:
- **File Operations**: Limited to safe file I/O operations
- **Code Executor**: Filters unsafe Python patterns (production needs sandboxing)
- **Calculator**: Uses safe expression evaluation
- **Web Search**: Currently mock implementation - replace with real APIs

When extending tools, implement proper input validation and rate limiting.
