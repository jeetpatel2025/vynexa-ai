import os
import sys
import asyncio

# Set environment variables
os.environ['OPENROUTER_API_KEY'] = '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'
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['LLM_MODEL'] = 'anthropic/claude-3-haiku:beta'

# Add current directory to path
sys.path.insert(0, '.')

from src.core.chatbot import ChatBot

async def test_memory():
    config = {
        'llm': {
            'provider': 'openrouter',
            'model': 'anthropic/claude-3-haiku:beta',
            'max_tokens': 4000,
            'temperature': 0.7,
        },
        'memory': {
            'db_path': 'data/memory.db',
            'vector_db_path': 'data/chroma_db'
        },
        'tools': {
            'enabled_tools': ['web_search', 'calculator', 'file_operations']
        },
        'reasoning': True
    }

    bot = ChatBot(config)

    # Test conversation with memory
    print("Testing memory management...")

    # First message
    response1 = await bot.process_message("My name is John and I like Python programming.", context={'session_id': 'test_session'})
    print(f"Response 1: {response1}")

    # Second message that should remember the first
    response2 = await bot.process_message("What's my name and what do I like?", context={'session_id': 'test_session'})
    print(f"Response 2: {response2}")

    # Test tool usage
    response3 = await bot.process_message("What is 15 + 27?", context={'session_id': 'test_session'})
    print(f"Response 3: {response3}")

    print("Memory test completed!")

if __name__ == '__main__':
    asyncio.run(test_memory())
