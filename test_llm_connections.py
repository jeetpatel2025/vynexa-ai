#!/usr/bin/env python3
"""
LLM Connection Testing Script
Tests connectivity and functionality for all supported LLM providers.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ai.llm_client import LLMClient
from config.config import Config

async def test_openai_connection():
    """Test OpenAI API connection."""
    print("🔍 Testing OpenAI connection...")
    
    config = {
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',  # Start with a cheaper model for testing
        'max_tokens': 100,
        'temperature': 0.7
    }
    
    try:
        client = LLMClient(config)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
            {"role": "user", "content": "Say 'Hello, OpenAI connection successful!' and nothing else."}
        ]
        
        response = await client.generate_response(messages)
        print(f"✅ OpenAI Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
        return False

async def test_anthropic_connection():
    """Test Anthropic API connection."""
    print("\n🔍 Testing Anthropic connection...")
    
    config = {
        'provider': 'anthropic',
        'model': 'claude-3-haiku-20240307',  # Cheapest Claude model
        'max_tokens': 100,
        'temperature': 0.7
    }
    
    try:
        client = LLMClient(config)
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant. Respond briefly."},
            {"role": "user", "content": "Say 'Hello, Anthropic connection successful!' and nothing else."}
        ]
        
        response = await client.generate_response(messages)
        print(f"✅ Anthropic Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Anthropic Error: {str(e)}")
        return False

async def test_local_model():
    """Test local model functionality."""
    print("\n🔍 Testing local model connection...")
    
    config = {
        'provider': 'local',
        'model': 'microsoft/DialoGPT-medium',  # Relatively small model for testing
        'max_tokens': 50,
        'temperature': 0.7
    }
    
    try:
        print("⏳ Loading local model (this may take a while on first run)...")
        client = LLMClient(config)
        
        messages = [
            {"role": "user", "content": "Hello, how are you?"}
        ]
        
        response = await client.generate_response(messages)
        print(f"✅ Local Model Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ Local Model Error: {str(e)}")
        print("💡 Tip: Local models require significant resources and may not work on all systems.")
        return False

async def test_chatbot_integration():
    """Test the full chatbot with different providers."""
    print("\n🔍 Testing ChatBot integration...")
    
    from src.core.chatbot import ChatBot
    
    # Test with OpenAI first (most likely to work)
    config = Config().get()
    
    try:
        bot = ChatBot(config)
        response = await bot.process_message("Hello! Can you tell me what 2+2 equals?")
        print(f"✅ ChatBot Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        return True
        
    except Exception as e:
        print(f"❌ ChatBot Error: {str(e)}")
        return False

async def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    config = Config()
    
    print(f"📋 Current configuration:")
    print(f"  - LLM Provider: {config.get('llm.provider')}")
    print(f"  - Model: {config.get('llm.model')}")
    print(f"  - OpenAI API Key: {'✅ Set' if config.get('llm.openai_api_key') else '❌ Not set'}")
    print(f"  - Anthropic API Key: {'✅ Set' if config.get('llm.anthropic_api_key') else '❌ Not set'}")
    print(f"  - Enabled Tools: {config.get('tools.enabled_tools')}")
    
    is_valid = config.validate()
    print(f"  - Configuration Valid: {'✅ Yes' if is_valid else '❌ No'}")
    
    return is_valid

async def main():
    """Main testing function."""
    print("🚀 LLM Connection Testing Suite")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    results = {}
    
    # Check environment first
    results['environment'] = await check_environment()
    
    if not results['environment']:
        print("\n⚠️  Configuration issues detected. Please check your .env file.")
        print("💡 Make sure to add your API keys to the .env file.")
        return
    
    # Test each provider
    if os.getenv('OPENAI_API_KEY'):
        results['openai'] = await test_openai_connection()
    else:
        print("\n⚠️  Skipping OpenAI test - no API key found")
        results['openai'] = False
    
    if os.getenv('ANTHROPIC_API_KEY'):
        results['anthropic'] = await test_anthropic_connection()
    else:
        print("\n⚠️  Skipping Anthropic test - no API key found")
        results['anthropic'] = False
    
    # Test local model (optional)
    print("\n❓ Test local model? This will download models and may take time. (y/N): ", end="")
    # For automated testing, skip local model
    results['local'] = False
    print("Skipping local model test for now.")
    
    # Test full chatbot integration if any provider works
    if any(results.values()):
        results['chatbot'] = await test_chatbot_integration()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name.capitalize()}: {status}")
    
    total_tests = len([r for r in results.values() if r is not False])
    passed_tests = sum(results.values())
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests > 0:
        print("🎉 Great! At least one LLM provider is working.")
        print("\n💡 Next steps:")
        print("  1. Run the CLI: python ui/cli/main.py chat -m 'Hello!'")
        print("  2. Or start the web interface: python ui/web/app.py")
    else:
        print("😞 No LLM providers are working. Check your API keys and configuration.")

if __name__ == "__main__":
    asyncio.run(main())
