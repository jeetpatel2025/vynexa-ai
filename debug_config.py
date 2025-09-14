import os
from unittest.mock import patch

# Test the config validation
with patch.dict(os.environ, {
    'LLM_PROVIDER': 'openai',
    'LLM_MODEL': 'gpt-4o',
    'OPENAI_API_KEY': 'test-key'
}):
    from config.config import Config

    config = Config()
    print("Config loaded:")
    print(f"Provider: {config.get('llm.provider')}")
    print(f"Model: {config.get('llm.model')}")
    print(f"API Key: {config.get('llm.openai_api_key')}")

    result = config.validate()
    print(f"Validation result: {result}")

    # Check what the validation is looking for
    required_keys = ['llm.provider', 'llm.model']
    provider = config.get('llm.provider')
    if provider == 'openai':
        required_keys.append('llm.openai_api_key')

    print(f"Required keys: {required_keys}")

    missing_keys = []
    for key in required_keys:
        value = config.get(key)
        print(f"Key '{key}': '{value}' (bool: {bool(value)})")
        if not value:
            missing_keys.append(key)

    print(f"Missing keys: {missing_keys}")
