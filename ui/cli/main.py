import os
import asyncio
from typing import Optional
import click
from dotenv import load_dotenv

from src.core.chatbot import ChatBot


@click.group()
def cli():
    """CLI for interacting with the AI Chatbot."""
    pass


def load_config():
    load_dotenv()
    return {
        'llm': {
            'provider': os.getenv('LLM_PROVIDER', 'openai'),
            'model': os.getenv('LLM_MODEL', 'gpt-4o'),
            'max_tokens': int(os.getenv('MAX_TOKENS', '4000')),
            'temperature': float(os.getenv('TEMPERATURE', '0.7')),
        },
        'memory': {
            'db_path': os.getenv('MEMORY_DB_PATH', 'data/memory.db'),
            'vector_db_path': os.getenv('VECTOR_DB_PATH', 'data/chroma_db')
        },
        'tools': {
            'enabled_tools': os.getenv('ENABLED_TOOLS', 'web_search,calculator,file_operations').split(',')
        },
        'reasoning': os.getenv('REASONING_ENABLED', 'true').lower() == 'true'
    }


@cli.command()
@click.option('--message', '-m', required=True, help='Message to send to the chatbot')
@click.option('--session', '-s', default='default', help='Session ID for conversation continuity')
def chat(message: str, session: str):
    """Send a message to the chatbot and print the response."""
    config = load_config()
    bot = ChatBot(config)

    async def run():
        response = await bot.process_message(message, context={'session_id': session})
        click.echo(response)

    asyncio.run(run())


@cli.command()
def tools():
    """List available tools."""
    config = load_config()
    bot = ChatBot(config)
    available = bot.tool_manager.get_available_tools()
    for tool in available:
        click.echo(f"- {tool['name']}: {tool['description']}")


if __name__ == '__main__':
    cli()

