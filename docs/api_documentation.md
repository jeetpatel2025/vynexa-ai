# API Documentation

This document provides detailed API documentation for the AI Chatbot project.

## Core Classes

### ChatBot

The main chatbot class that orchestrates all AI functionality.

```python
from src.core.chatbot import ChatBot

class ChatBot:
    def __init__(self, config: Dict[str, Any])
    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> str
    def reset_conversation(self)
```

#### Methods

##### `__init__(config: Dict[str, Any])`
Initialize the chatbot with configuration.

**Parameters:**
- `config`: Configuration dictionary containing LLM, memory, and tool settings

**Example:**
```python
config = {
    'llm': {
        'provider': 'openai',
        'model': 'gpt-4o',
        'max_tokens': 4000,
        'temperature': 0.7
    },
    'memory': {
        'db_path': 'data/memory.db',
        'vector_db_path': 'data/chroma_db'
    },
    'tools': {
        'enabled_tools': ['web_search', 'calculator']
    },
    'reasoning': True
}
bot = ChatBot(config)
```

##### `async process_message(user_message: str, context: Optional[Dict] = None) -> str`
Process a user message and generate a response.

**Parameters:**
- `user_message`: The input message from the user
- `context`: Optional context dictionary (session_id, user preferences, etc.)

**Returns:**
- Generated response string

**Example:**
```python
response = await bot.process_message(
    "What is machine learning?",
    context={'session_id': 'user123'}
)
```

##### `reset_conversation()`
Reset the current conversation history.

### LLMClient

Unified client for multiple LLM providers.

```python
from src.ai.llm_client import LLMClient

class LLMClient:
    def __init__(self, config: Dict[str, Any])
    async def generate_response(self, messages: List[Dict[str, str]], tools: Optional[List[str]] = None) -> str
    async def analyze_image(self, image_path: str, prompt: str) -> str
    def supports_multimodal(self) -> bool
```

#### Methods

##### `async generate_response(messages: List[Dict[str, str]], tools: Optional[List[str]] = None) -> str`
Generate a response using the configured LLM.

**Parameters:**
- `messages`: List of conversation messages in OpenAI format
- `tools`: Optional list of available tools

**Returns:**
- Generated response text

**Example:**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]
response = await llm_client.generate_response(messages)
```

##### `async analyze_image(image_path: str, prompt: str) -> str`
Analyze an image with a text prompt (if multimodal support is available).

**Parameters:**
- `image_path`: Path to the image file
- `prompt`: Text prompt for image analysis

**Returns:**
- Analysis result text

### MemoryManager

Advanced memory management for long-term context.

```python
from src.ai.memory_manager import MemoryManager

class MemoryManager:
    def __init__(self, config: Dict[str, Any])
    async def store_interaction(self, user_message: str, assistant_response: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None)
    async def retrieve_memories(self, query: str, limit: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]
    async def get_conversation_context(self, session_id: str, max_tokens: int = 2000) -> List[Dict[str, str]]
    async def store_user_preference(self, key: str, value: str)
    async def get_user_preference(self, key: str) -> Optional[str]
```

#### Methods

##### `async store_interaction(...)`
Store a conversation interaction in memory.

**Parameters:**
- `user_message`: User's input
- `assistant_response`: Assistant's response
- `session_id`: Optional session identifier
- `metadata`: Additional metadata

##### `async retrieve_memories(query: str, limit: int = 5, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]`
Retrieve relevant memories based on semantic similarity.

**Parameters:**
- `query`: Query text to find similar conversations
- `limit`: Maximum number of memories to retrieve
- `similarity_threshold`: Minimum similarity score (0.0-1.0)

**Returns:**
- List of relevant conversation memories

**Example:**
```python
memories = await memory.retrieve_memories("programming languages", limit=3)
for memory in memories:
    print(f"Similarity: {memory['similarity']}")
    print(f"Content: {memory['content']}")
```

### ToolManager

Tool management system for function calling.

```python
from src.ai.tool_manager import ToolManager

class ToolManager:
    def __init__(self, config: Dict[str, Any])
    async def analyze_tool_need(self, user_message: str) -> List[str]
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]
    def register_tool(self, name: str, func: Callable, description: str)
    def get_available_tools(self) -> List[Dict[str, Any]]
```

#### Methods

##### `async analyze_tool_need(user_message: str) -> List[str]`
Analyze if tools are needed based on user message.

**Parameters:**
- `user_message`: User's input message

**Returns:**
- List of tool names that might be useful

##### `async execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]`
Execute a specific tool with parameters.

**Parameters:**
- `tool_name`: Name of the tool to execute
- `**kwargs`: Tool-specific parameters

**Returns:**
- Tool execution result dictionary

**Example:**
```python
result = await tool_manager.execute_tool('calculator', expression='2+2')
if result['success']:
    print(result['result'])
```

## Built-in Tools

### Calculator
Performs mathematical calculations.

**Usage:**
```python
result = await tool_manager.execute_tool('calculator', expression='sqrt(16) + 2*3')
```

### Web Search
Searches the web for current information.

**Usage:**
```python
result = await tool_manager.execute_tool('web_search', query='latest AI news', num_results=5)
```

### File Operations
Read, write, and manage files.

**Usage:**
```python
# Read file
result = await tool_manager.execute_tool('file_operations', operation='read', filepath='data.txt')

# Write file
result = await tool_manager.execute_tool('file_operations', operation='write', filepath='output.txt', content='Hello World')
```

### Weather
Get weather information for a location.

**Usage:**
```python
result = await tool_manager.execute_tool('weather', location='New York')
```

### DateTime
Get current date and time information.

**Usage:**
```python
result = await tool_manager.execute_tool('datetime', timezone='UTC')
```

## Configuration Schema

### Complete Configuration Example

```python
config = {
    'llm': {
        'provider': 'openai',  # 'openai', 'anthropic', or 'local'
        'model': 'gpt-4o',
        'openai_api_key': 'sk-...',
        'anthropic_api_key': 'sk-ant-...',
        'max_tokens': 4000,
        'temperature': 0.7
    },
    'memory': {
        'db_path': 'data/memory.db',
        'vector_db_path': 'data/chroma_db',
        'max_context_length': 10000
    },
    'tools': {
        'enabled_tools': [
            'web_search',
            'calculator', 
            'file_operations',
            'weather',
            'datetime',
            'code_executor'
        ],
        'openweather_api_key': 'your_api_key',
        'google_search_api_key': 'your_api_key',
        'google_search_engine_id': 'your_engine_id'
    },
    'reasoning': True,
    'web': {
        'secret_key': 'your-secret-key',
        'host': '127.0.0.1',
        'port': 5000,
        'debug': False
    },
    'logging': {
        'level': 'INFO',
        'file': 'logs/chatbot.log'
    }
}
```

## Error Handling

All async methods can raise exceptions. Common exceptions include:

- `ValueError`: Invalid configuration or parameters
- `ConnectionError`: Network or API connection issues
- `FileNotFoundError`: Missing files or directories
- `sqlite3.Error`: Database-related errors

**Example error handling:**
```python
try:
    response = await bot.process_message("Hello")
except ValueError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Custom Tool Development

### Creating a Custom Tool

1. Define the tool function:

```python
async def my_custom_tool(self, param1: str, param2: int = 10) -> str:
    """
    Custom tool that processes input parameters.
    
    Args:
        param1: A string parameter
        param2: An integer parameter with default value
        
    Returns:
        Processed result as string
    """
    # Your tool logic here
    result = f"Processed {param1} with value {param2}"
    return result
```

2. Register the tool:

```python
tool_manager.register_tool(
    'my_custom_tool',
    my_custom_tool,
    'Description of what my custom tool does'
)
```

3. Add pattern matching (optional):

```python
# In analyze_tool_need method, add patterns for your tool
tool_patterns = {
    'my_custom_tool': [
        r'custom process', r'my tool', r'special function'
    ]
}
```

### Tool Integration Example

```python
from src.ai.tool_manager import ToolManager
import requests

class CustomToolManager(ToolManager):
    def _register_builtin_tools(self):
        super()._register_builtin_tools()
        self.register_tool('crypto_price', self._crypto_price, 
                          "Get cryptocurrency prices")
    
    async def _crypto_price(self, symbol: str) -> str:
        """Get cryptocurrency price from an API."""
        try:
            response = requests.get(f'https://api.coindesk.com/v1/bpi/currentprice/{symbol}.json')
            data = response.json()
            price = data['bpi'][symbol.upper()]['rate']
            return f"{symbol.upper()} price: {price}"
        except Exception as e:
            return f"Error fetching price: {str(e)}"

# Usage
config = {'enabled_tools': ['crypto_price']}
tool_manager = CustomToolManager(config)
result = await tool_manager.execute_tool('crypto_price', symbol='btc')
```

## Performance Considerations

- **Memory Usage**: The vector database can grow large over time. Use `cleanup_old_memories()` periodically
- **API Limits**: Be aware of rate limits for external APIs (OpenAI, Anthropic, etc.)
- **Concurrency**: The system supports multiple concurrent sessions but shares resources
- **Caching**: Consider implementing response caching for expensive operations

## Security Notes

- **API Keys**: Store API keys securely in environment variables, never in code
- **File Operations**: The file operations tool has basic safety checks but should be used carefully
- **Code Execution**: The code executor has safety restrictions but should not be used in production without sandboxing
- **User Input**: All user inputs are processed by LLMs - implement additional validation for sensitive applications
