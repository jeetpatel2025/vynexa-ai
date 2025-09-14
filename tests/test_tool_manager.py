import pytest
import asyncio
from unittest.mock import Mock, patch
from src.ai.tool_manager import ToolManager


class TestToolManager:
    """Test tool manager functionality."""

    @pytest.fixture
    def config(self):
        return {
            'enabled_tools': ['calculator', 'web_search']
        }

    def test_tool_registration(self, config):
        """Test tool registration and availability."""
        manager = ToolManager(config)

        # Check that built-in tools are registered
        assert 'calculator' in manager.tools
        assert 'web_search' in manager.tools
        assert 'file_operations' in manager.tools

        # Check enabled tools
        available = manager.get_available_tools()
        tool_names = [tool['name'] for tool in available]

        assert 'calculator' in tool_names
        assert 'web_search' in tool_names
        assert 'file_operations' not in tool_names  # Not enabled

    @pytest.mark.asyncio
    async def test_calculator_tool(self, config):
        """Test calculator tool execution."""
        manager = ToolManager(config)

        result = await manager.execute_tool('calculator', expression='2 + 3')
        assert result['success'] == True
        assert '5' in result['result']

    @pytest.mark.asyncio
    async def test_web_search_tool(self, config):
        """Test web search tool (mocked)."""
        manager = ToolManager(config)

        result = await manager.execute_tool('web_search', query='test query')
        assert result['success'] == True
        assert 'Web search results for' in result['result']
        assert 'test query' in result['result']
        assert 'Mock result' in result['result']

    def test_tool_enabling_disabling(self, config):
        """Test enabling and disabling tools."""
        manager = ToolManager(config)

        # Initially calculator should be enabled
        assert manager.tools['calculator']['enabled']

        # Disable calculator
        manager.disable_tool('calculator')
        assert not manager.tools['calculator']['enabled']

        # Enable calculator
        manager.enable_tool('calculator')
        assert manager.tools['calculator']['enabled']

    @pytest.mark.asyncio
    async def test_tool_need_analysis(self, config):
        """Test tool need analysis based on user messages."""
        manager = ToolManager(config)

        # Message that should trigger calculator
        tools = await manager.analyze_tool_need("What is 15 + 27?")
        assert 'calculator' in tools

        # Message that should trigger web search
        tools = await manager.analyze_tool_need("Search for latest AI news")
        assert 'web_search' in tools

        # Regular message should not trigger tools
        tools = await manager.analyze_tool_need("Hello, how are you?")
        assert len(tools) == 0
