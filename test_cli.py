import os
import sys
import asyncio

# Set environment variables
os.environ['OPENROUTER_API_KEY'] = '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'
os.environ['LLM_PROVIDER'] = 'openrouter'
os.environ['LLM_MODEL'] = 'anthropic/claude-3-haiku:beta'

# Add current directory to path
sys.path.insert(0, '.')

from ui.cli.main import cli

if __name__ == '__main__':
    cli(['chat', '-m', 'Hello, can you introduce yourself?'])
