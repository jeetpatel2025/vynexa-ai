# Warp AI Integration Guide

This guide covers all four aspects of connecting your AI chatbot with Warp's LLM capabilities:

## 1. Testing Your Chatbot's LLM Connection ✅

Your chatbot now supports multiple LLM providers with enhanced capabilities:

### Supported Providers:
- **OpenAI**: GPT-4, GPT-3.5-turbo with function calling
- **Anthropic**: Claude models (Haiku, Sonnet, Opus)
- **Local Models**: HuggingFace transformers
- **Ollama**: Local server for models like Llama, Mistral, etc.

### Test All Connections:
```bash
python test_llm_connections.py
```

This script will:
- ✅ Validate your environment configuration
- ✅ Test OpenAI connection (if API key provided)
- ✅ Test Anthropic connection (if API key provided)
- ✅ Test local models (optional)
- ✅ Test full chatbot integration

## 2. Configuring Different LLM Providers ✅

### Setup API Keys:
Edit your `.env` file with real API keys:

```env
# OpenAI Setup
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-your-real-openai-key-here

# OR Anthropic Setup
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
ANTHROPIC_API_KEY=sk-ant-your-real-anthropic-key-here

# OR Ollama Local Setup
LLM_PROVIDER=ollama
LLM_MODEL=llama2
```

### Switch Between Providers:
```bash
# Switch to OpenAI in PowerShell
$env:LLM_PROVIDER='openai'; $env:LLM_MODEL='gpt-4o'

# Switch to Anthropic
$env:LLM_PROVIDER='anthropic'; $env:LLM_MODEL='claude-3-haiku-20240307'

# Switch to Ollama (requires Ollama server running)
$env:LLM_PROVIDER='ollama'; $env:LLM_MODEL='llama2'
```

## 3. Integrating with Warp's AI Capabilities 

### Using Your Chatbot in Warp Agent Mode:

1. **Direct CLI Integration**:
   ```bash
   # Single message
   python ui/cli/main.py chat -m "Analyze this code and suggest improvements"
   
   # With session continuity
   python ui/cli/main.py chat -m "Hello" -s "work_session"
   ```

2. **Warp Integration Helper**:
   ```bash
   # Demo integration capabilities
   python warp_integration.py demo
   
   # Chat with context awareness
   python warp_integration.py chat -m "Help me debug this error"
   
   # Generate Warp workflow
   python warp_integration.py workflow
   ```

### Advanced Integration Features:

**Context-Aware Processing**: The chatbot automatically receives Warp context:
- Current working directory
- Operating system information
- Shell type and version
- Environment variables

**Tool Integration**: Your chatbot tools work seamlessly with Warp:
- **File Operations**: Read/write files in your current directory
- **Calculator**: Mathematical computations for development
- **Web Search**: Look up documentation and solutions
- **Code Execution**: Safe Python code execution
- **Weather/DateTime**: Contextual information

### Creating Warp Workflows:

Generate a complete Warp workflow configuration:
```bash
python warp_integration.py workflow > ai_chatbot_workflow.json
```

This creates shortcuts for:
- Quick AI chat
- Provider switching
- Tool management
- Web interface launch

## 4. Local LLM Support ✅

### Option A: HuggingFace Transformers
```env
LLM_PROVIDER=local
LLM_MODEL=microsoft/DialoGPT-medium
```

### Option B: Ollama Server (Recommended)
1. Install Ollama: https://ollama.ai
2. Start Ollama server:
   ```bash
   ollama serve
   ```
3. Pull a model:
   ```bash
   ollama pull llama2
   ```
4. Configure your chatbot:
   ```env
   LLM_PROVIDER=ollama
   LLM_MODEL=llama2
   OLLAMA_BASE_URL=http://localhost:11434
   ```

### Available Local Models:
- **Llama 2/3**: General purpose chat
- **Code Llama**: Specialized for code
- **Mistral**: Fast and efficient
- **Phi**: Microsoft's small model
- **Neural Chat**: Intel's optimized model

## Using Your Enhanced Chatbot

### Quick Start:
1. **Set up API keys** in `.env`
2. **Test connections**: `python test_llm_connections.py`
3. **Start chatting**: `python ui/cli/main.py chat -m "Hello!"`
4. **Launch web interface**: `python ui/web/app.py`

### Advanced Usage:

**Tool-Specific Queries**:
```bash
# Mathematical calculation
python ui/cli/main.py chat -m "Calculate the compound interest on $1000 at 5% for 10 years"

# File operations
python ui/cli/main.py chat -m "Read the README.md file and summarize it"

# Web search
python ui/cli/main.py chat -m "Search for the latest Python 3.13 features"
```

**Session Management**:
```bash
# Maintain conversation context
python ui/cli/main.py chat -m "My name is John" -s "personal"
python ui/cli/main.py chat -m "What's my name?" -s "personal"  # Remembers!
```

**Provider Comparison**:
```bash
# Test same query across providers
LLM_PROVIDER=openai python ui/cli/main.py chat -m "Explain quantum computing"
LLM_PROVIDER=anthropic python ui/cli/main.py chat -m "Explain quantum computing"
LLM_PROVIDER=ollama python ui/cli/main.py chat -m "Explain quantum computing"
```

## Troubleshooting

### Common Issues:

1. **API Key Errors**: 
   - Verify keys in `.env` file
   - Check account credits/limits

2. **ChromaDB Timeout**:
   - First run downloads models (patient required)
   - Restart if connection times out

3. **Ollama Connection Failed**:
   - Ensure Ollama server is running: `ollama serve`
   - Check port availability (default: 11434)

4. **Import Errors**:
   - Run: `pip install -r requirements.txt`
   - Ensure all dependencies installed

### Performance Tips:

- **OpenAI**: Fastest responses, pay-per-use
- **Anthropic**: Good balance of speed/quality
- **Ollama**: Free but requires good hardware
- **HuggingFace**: Slowest but completely local

## Integration with Warp Agent Mode

Your chatbot is now ready to work seamlessly with Warp's Agent Mode:

1. **Context Awareness**: Automatically receives your current environment context
2. **Tool Integration**: All tools work within Warp's terminal environment  
3. **Memory Persistence**: Maintains conversation history across Warp sessions
4. **Provider Flexibility**: Switch between cloud and local models as needed

The `warp_integration.py` script provides the bridge between your sophisticated AI chatbot and Warp's agent capabilities, giving you the best of both worlds!
