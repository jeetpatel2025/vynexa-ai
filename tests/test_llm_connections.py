import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from src.ai.llm_client import LLMClient


class TestLLMClient:
    """Test LLM client functionality."""

    @pytest.fixture
    def config(self):
        return {
            'provider': 'openrouter',
            'model': 'gpt-4o',
            'max_tokens': 1000,
            'temperature': 0.7,
            'openrouter_api_key': 'test-key'
        }

    @pytest.mark.asyncio
    async def test_openai_connection(self, config):
        """Test OpenAI client initialization and basic functionality."""
        with patch('openai.AsyncOpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client

            # Mock response
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response"
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            client = LLMClient(config)

            # Test basic response generation
            messages = [{"role": "user", "content": "Hello"}]
            response = await client.generate_response(messages)

            assert response == "Test response"
            mock_client.chat.completions.create.assert_called_once()

    def test_supported_providers(self, config):
        """Test that supported providers are correctly listed."""
        client = LLMClient(config)
        providers = client.get_supported_providers()

        assert 'openai' in providers
        assert 'anthropic' in providers
        assert 'local' in providers
        assert 'ollama' in providers

    def test_multimodal_support(self, config):
        """Test multimodal support detection."""
        # OpenAI with vision model should support multimodal
        config_vision = config.copy()
        config_vision['model'] = 'gpt-4-vision-preview'

        with patch('openai.AsyncOpenAI'):
            client = LLMClient(config_vision)
            assert client.supports_multimodal()

        # Regular GPT model should not support multimodal
        with patch('openai.AsyncOpenAI'):
            client = LLMClient(config)
            assert not client.supports_multimodal()
