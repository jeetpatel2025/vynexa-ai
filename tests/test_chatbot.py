import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.core.chatbot import ChatBot
from src.core.conversation import Conversation


class TestChatBot:
    """Test chatbot core functionality."""

    @pytest.fixture
    def config(self):
        return {
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4o',
                'max_tokens': 1000,
                'temperature': 0.7
            },
            'memory': {
                'db_path': ':memory:',  # Use in-memory SQLite
                'vector_db_path': 'data/test_chroma'
            },
            'tools': {
                'enabled_tools': ['calculator']
            },
            'reasoning': True
        }

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        mock_client = Mock()
        mock_client.generate_response = AsyncMock(return_value="Mock response")
        return mock_client

    @pytest.fixture
    def mock_memory_manager(self):
        """Mock memory manager."""
        mock_memory = Mock()
        mock_memory.retrieve_memories = AsyncMock(return_value=[])
        mock_memory.store_interaction = AsyncMock()
        return mock_memory

    @pytest.fixture
    def mock_tool_manager(self):
        """Mock tool manager."""
        mock_tools = Mock()
        mock_tools.analyze_tool_need = AsyncMock(return_value=[])
        return mock_tools

    @pytest.mark.asyncio
    async def test_chatbot_initialization(self, config):
        """Test chatbot initialization."""
        with patch('src.core.chatbot.LLMClient') as mock_llm_class, \
             patch('src.core.chatbot.MemoryManager') as mock_memory_class, \
             patch('src.core.chatbot.ToolManager') as mock_tool_class, \
             patch('src.ai.memory_manager.chromadb.PersistentClient') as mock_chroma:

            mock_llm_class.return_value = Mock()
            mock_memory_class.return_value = Mock()
            mock_tool_class.return_value = Mock()
            mock_chroma.return_value = Mock()

            bot = ChatBot(config)

            assert bot.config == config
            assert isinstance(bot.conversation, Conversation)
            mock_llm_class.assert_called_once_with(config.get('llm', {}))
            mock_memory_class.assert_called_once_with(config.get('memory', {}))
            mock_tool_class.assert_called_once_with(config.get('tools', {}))

    @pytest.mark.asyncio
    async def test_process_message_basic(self, config, mock_llm_client, mock_memory_manager, mock_tool_manager):
        """Test basic message processing."""
        with patch('src.core.chatbot.LLMClient', return_value=mock_llm_client), \
             patch('src.core.chatbot.MemoryManager', return_value=mock_memory_manager), \
             patch('src.core.chatbot.ToolManager', return_value=mock_tool_manager), \
             patch('src.ai.memory_manager.chromadb.PersistentClient') as mock_chroma:

            mock_chroma.return_value = Mock()
            bot = ChatBot(config)

            response = await bot.process_message("Hello, how are you?")

            assert response == "Mock response"
            assert len(bot.conversation.messages) == 2  # User + Assistant
            assert bot.conversation.messages[0].content == "Hello, how are you?"
            assert bot.conversation.messages[1].content == "Mock response"

            # Verify memory operations were called
            mock_memory_manager.retrieve_memories.assert_called_once_with("Hello, how are you?")
            mock_memory_manager.store_interaction.assert_called_once_with("Hello, how are you?", "Mock response")

    @pytest.mark.asyncio
    async def test_process_message_with_tools(self, config, mock_llm_client, mock_memory_manager, mock_tool_manager):
        """Test message processing with tool usage."""
        mock_tool_manager.analyze_tool_need.return_value = ['calculator']

        with patch('src.core.chatbot.LLMClient', return_value=mock_llm_client), \
             patch('src.core.chatbot.MemoryManager', return_value=mock_memory_manager), \
             patch('src.core.chatbot.ToolManager', return_value=mock_tool_manager), \
             patch('src.ai.memory_manager.chromadb.PersistentClient') as mock_chroma:

            mock_chroma.return_value = Mock()
            bot = ChatBot(config)

            response = await bot.process_message("What is 2 + 3?")

            # Verify tool analysis was called
            mock_tool_manager.analyze_tool_need.assert_called_once_with("What is 2 + 3?")

            # Verify LLM was called with tools parameter
            mock_llm_client.generate_response.assert_called_once()
            call_args = mock_llm_client.generate_response.call_args
            messages, tools = call_args[0]
            assert tools == ['calculator']

    def test_conversation_reset(self, config):
        """Test conversation reset functionality."""
        with patch('src.core.chatbot.LLMClient'), \
             patch('src.core.chatbot.MemoryManager'), \
             patch('src.core.chatbot.ToolManager'), \
             patch('src.ai.memory_manager.chromadb.PersistentClient') as mock_chroma:

            mock_chroma.return_value = Mock()
            bot = ChatBot(config)

            # Add some messages
            bot.conversation.add('user', 'Hello')
            bot.conversation.add('assistant', 'Hi there')

            assert len(bot.conversation.messages) == 2

            # Reset conversation
            bot.reset_conversation()

            assert len(bot.conversation.messages) == 0
            assert isinstance(bot.conversation, Conversation)

    @pytest.mark.asyncio
    async def test_system_prompt_building(self, config, mock_llm_client, mock_memory_manager, mock_tool_manager):
        """Test system prompt building with context."""
        mock_memory_manager.retrieve_memories.return_value = [
            {'content': 'Previous conversation', 'role': 'user'}
        ]

        with patch('src.core.chatbot.LLMClient', return_value=mock_llm_client), \
             patch('src.core.chatbot.MemoryManager', return_value=mock_memory_manager), \
             patch('src.core.chatbot.ToolManager', return_value=mock_tool_manager), \
             patch('src.ai.memory_manager.chromadb.PersistentClient') as mock_chroma:

            mock_chroma.return_value = Mock()
            bot = ChatBot(config)

            await bot.process_message("Test message", context={'session_id': 'test'})

            # Verify LLM was called
            mock_llm_client.generate_response.assert_called_once()
            call_args = mock_llm_client.generate_response.call_args
            messages = call_args[0][0]

            # Check system message
            system_message = messages[0]
            assert system_message['role'] == 'system'
            assert 'GPT-5-like capabilities' in system_message['content']
            assert 'Previous conversation' in system_message['content']
