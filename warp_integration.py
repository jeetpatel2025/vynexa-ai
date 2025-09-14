#!/usr/bin/env python3
"""
Warp AI Integration Helper
Provides utilities for integrating the AI Chatbot with Warp's Agent Mode.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.chatbot import ChatBot
from config.config import Config

class WarpAIIntegration:
    """Integration layer between AI Chatbot and Warp Agent Mode."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with configuration."""
        if config is None:
            config = Config().get()
        
        self.chatbot = ChatBot(config)
        self.config = config
    
    async def process_warp_command(self, command: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a command from Warp Agent Mode.
        
        Args:
            command: The command/query from Warp
            context: Optional context (current directory, environment, etc.)
            
        Returns:
            Structured response for Warp
        """
        try:
            # Add Warp-specific context to the message
            if context:
                enhanced_command = f"""
                Context:
                - Current Directory: {context.get('pwd', 'unknown')}
                - Operating System: {context.get('os', 'unknown')}
                - Shell: {context.get('shell', 'unknown')}
                
                User Request: {command}
                """
            else:
                enhanced_command = command
            
            # Process through our chatbot
            response = await self.chatbot.process_message(
                enhanced_command,
                context={'source': 'warp_agent', **(context or {})}
            )
            
            return {
                'success': True,
                'response': response,
                'provider': self.config.get('llm', {}).get('provider', 'unknown'),
                'model': self.config.get('llm', {}).get('model', 'unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"Error processing request: {str(e)}"
            }
    
    async def get_tool_suggestions(self, query: str) -> Dict[str, Any]:
        """Get tool suggestions for a given query."""
        try:
            tools_needed = await self.chatbot.tool_manager.analyze_tool_need(query)
            available_tools = self.chatbot.tool_manager.get_available_tools()
            
            return {
                'success': True,
                'needed_tools': tools_needed,
                'available_tools': available_tools
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def execute_with_tools(self, query: str, allowed_tools: Optional[list] = None) -> Dict[str, Any]:
        """Execute query with specific tools allowed."""
        try:
            # Temporarily modify enabled tools if specified
            original_tools = self.chatbot.tool_manager.enabled_tools.copy()
            
            if allowed_tools:
                self.chatbot.tool_manager.enabled_tools = [
                    tool for tool in original_tools if tool in allowed_tools
                ]
            
            response = await self.chatbot.process_message(query)
            
            # Restore original tools
            self.chatbot.tool_manager.enabled_tools = original_tools
            
            return {
                'success': True,
                'response': response,
                'tools_used': allowed_tools or original_tools
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def create_warp_workflow():
    """Create a Warp workflow for AI chatbot integration."""
    
    workflow = {
        "name": "AI Chatbot Integration",
        "description": "Use the advanced AI chatbot with reasoning and tools",
        "commands": [
            {
                "name": "Chat with AI",
                "command": "python test_llm_connections.py && python ui/cli/main.py chat -m \"{{message}}\"",
                "description": "Send a message to the AI chatbot"
            },
            {
                "name": "Test LLM Connections",
                "command": "python test_llm_connections.py",
                "description": "Test all LLM provider connections"
            },
            {
                "name": "Start Web Interface",
                "command": "python ui/web/app.py",
                "description": "Launch the web-based chat interface"
            },
            {
                "name": "List Available Tools",
                "command": "python ui/cli/main.py tools",
                "description": "Show all available AI tools"
            },
            {
                "name": "Switch to OpenAI",
                "command": "$env:LLM_PROVIDER='openai'; $env:LLM_MODEL='gpt-4o'",
                "description": "Switch to OpenAI GPT-4"
            },
            {
                "name": "Switch to Anthropic",
                "command": "$env:LLM_PROVIDER='anthropic'; $env:LLM_MODEL='claude-3-sonnet-20240229'",
                "description": "Switch to Anthropic Claude"
            },
            {
                "name": "Switch to Local (Ollama)",
                "command": "$env:LLM_PROVIDER='ollama'; $env:LLM_MODEL='llama2'",
                "description": "Switch to local Ollama model"
            }
        ]
    }
    
    return workflow

async def demo_integration():
    """Demonstrate the Warp integration capabilities."""
    print("🤖 Warp AI Integration Demo")
    print("=" * 40)
    
    # Initialize integration
    integration = WarpAIIntegration()
    
    # Test basic functionality
    print("\\n1. Testing basic AI response...")
    result = await integration.process_warp_command(
        "Hello! Can you explain what you are and what tools you have available?",
        context={
            'pwd': 'C:\\\\Users\\\\user\\\\project',
            'os': 'Windows',
            'shell': 'PowerShell'
        }
    )
    
    if result['success']:
        print(f"✅ Response: {result['response'][:200]}{'...' if len(result['response']) > 200 else ''}")
        print(f"🔧 Provider: {result['provider']} ({result['model']})")
    else:
        print(f"❌ Error: {result['error']}")
    
    # Test tool suggestions
    print("\\n2. Testing tool suggestions...")
    tools_result = await integration.get_tool_suggestions(
        "I need to calculate the area of a circle with radius 5 and then search for information about pi"
    )
    
    if tools_result['success']:
        print(f"🛠️ Suggested tools: {', '.join(tools_result['needed_tools'])}")
        print(f"📋 Available tools: {len(tools_result['available_tools'])} total")
    else:
        print(f"❌ Error: {tools_result['error']}")
    
    # Test restricted tool execution
    print("\\n3. Testing restricted tool execution...")
    restricted_result = await integration.execute_with_tools(
        "What's 15% of 200?",
        allowed_tools=['calculator']
    )
    
    if restricted_result['success']:
        print(f"✅ Calculation result: {restricted_result['response']}")
    else:
        print(f"❌ Error: {restricted_result['error']}")
    
    print("\\n🎉 Integration demo complete!")

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Warp AI Integration Helper")
    parser.add_argument('action', choices=['demo', 'workflow', 'chat'], 
                       help='Action to perform')
    parser.add_argument('--message', '-m', type=str, 
                       help='Message for chat action')
    
    args = parser.parse_args()
    
    if args.action == 'demo':
        asyncio.run(demo_integration())
    elif args.action == 'workflow':
        workflow = create_warp_workflow()
        print(json.dumps(workflow, indent=2))
    elif args.action == 'chat':
        if not args.message:
            print("Error: --message required for chat action")
            return
        
        async def chat():
            integration = WarpAIIntegration()
            result = await integration.process_warp_command(args.message)
            if result['success']:
                print(result['response'])
            else:
                print(f"Error: {result['error']}")
        
        asyncio.run(chat())

if __name__ == "__main__":
    main()
