import os
from typing import Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the AI Chatbot project."""
    
    def __init__(self, env_path: str = '.env'):
        """Initialize configuration by loading environment variables."""
        load_dotenv(env_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load all configuration from environment variables."""
        return {
            'llm': {
                'provider': os.getenv('LLM_PROVIDER', 'openrouter'),
                'model': os.getenv('LLM_MODEL', 'gpt-4o'),
                'openai_api_key': os.getenv('OPENAI_API_KEY'),
                'openrouter_api_key': os.getenv('OPENROUTER_API_KEY'),
                'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
                'max_tokens': int(os.getenv('MAX_TOKENS', '4000')),
                'temperature': float(os.getenv('TEMPERATURE', '0.7')),
            },
            'memory': {
                'db_path': os.getenv('MEMORY_DB_PATH', 'data/memory.db'),
                'vector_db_path': os.getenv('VECTOR_DB_PATH', 'data/chroma_db'),
                'max_context_length': int(os.getenv('MAX_CONTEXT_LENGTH', '10000')),
            },
            'tools': {
                'enabled_tools': os.getenv('ENABLED_TOOLS', 'web_search,calculator,file_operations').split(','),
                'openweather_api_key': os.getenv('OPENWEATHER_API_KEY'),
                'google_search_api_key': os.getenv('GOOGLE_SEARCH_API_KEY'),
                'google_search_engine_id': os.getenv('GOOGLE_SEARCH_ENGINE_ID'),
            },
            'web': {
                'secret_key': os.getenv('SECRET_KEY', 'default-secret-key'),
                'host': os.getenv('HOST', '127.0.0.1'),
                'port': int(os.getenv('PORT', '5000')),
                'debug': os.getenv('DEBUG', 'false').lower() == 'true',
            },
            'reasoning': os.getenv('REASONING_ENABLED', 'true').lower() == 'true',
            'logging': {
                'level': os.getenv('LOG_LEVEL', 'INFO'),
                'file': os.getenv('LOG_FILE', 'logs/chatbot.log'),
            }
        }
    
    def get(self, key: str = None) -> Any:
        """Get configuration value by key or entire config if no key provided."""
        if key is None:
            return self._config
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def validate(self) -> bool:
        """Validate that required configuration is present and properly formatted."""
        required_keys = [
            'llm.provider',
            'llm.model',
        ]

        # Check for API keys based on provider
        provider = self.get('llm.provider')
        if provider == 'openai':
            required_keys.append('llm.openai_api_key')
        elif provider == 'openrouter':
            required_keys.append('llm.openrouter_api_key')
        elif provider == 'anthropic':
            required_keys.append('llm.anthropic_api_key')

        missing_keys = []
        invalid_keys = []
        for key in required_keys:
            value = self.get(key)
            if not value:
                missing_keys.append(key)
            elif key.endswith('_api_key') and not self._is_valid_api_key(value):
                invalid_keys.append(key)

        if missing_keys:
            print(f"Missing required configuration: {', '.join(missing_keys)}")
            return False

        if invalid_keys:
            print(f"Invalid API key format: {', '.join(invalid_keys)}")
            return False

        return True

    def _is_valid_api_key(self, api_key: str) -> bool:
        """Check if API key has a valid format."""
        if not api_key or len(api_key) < 10:
            return False

        # Check for common API key patterns
        if api_key.startswith('sk-') and len(api_key) > 20:  # OpenAI format
            return True
        if api_key.startswith('sk-or-v1-'):  # OpenRouter format
            return True
        if api_key.startswith('sk-ant-'):  # Anthropic format
            return True

        # For other providers, just check it's not obviously invalid
        return not api_key.startswith('test-') and not api_key == 'test-key'
    
    def create_directories(self):
        """Create necessary directories for the application."""
        directories = [
            self.get('memory.db_path').rsplit('/', 1)[0] if '/' in self.get('memory.db_path') else 'data',
            self.get('memory.vector_db_path'),
            self.get('logging.file').rsplit('/', 1)[0] if '/' in self.get('logging.file') else 'logs',
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Create a global config instance
config = Config()
