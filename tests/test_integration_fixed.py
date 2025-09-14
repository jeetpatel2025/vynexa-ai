import pytest
import subprocess
import time
import requests
import os
from unittest.mock import patch


class TestIntegration:
    """Integration tests for CLI and web interfaces."""

    def test_cli_import(self):
        """Test that CLI module can be imported."""
        try:
            from ui.cli.main import cli
            assert cli is not None
        except ImportError as e:
            pytest.fail(f"CLI import failed: {e}")

    def test_web_app_import(self):
        """Test that web app can be imported."""
        try:
            from ui.web.app import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Web app import failed: {e}")

    def test_config_import(self):
        """Test that config module can be imported."""
        try:
            from config.config import config
            assert config is not None
        except ImportError as e:
            pytest.fail(f"Config import failed: {e}")

    @patch.dict(os.environ, {
        'LLM_PROVIDER': 'openai',
        'LLM_MODEL': 'gpt-4o',
        'OPENAI_API_KEY': 'test-key'
    })
    def test_config_validation(self):
        """Test configuration validation."""
        from config.config import Config

        config = Config()
        # Should not validate without proper API key format
        assert not config.validate()

        # With proper API key format it should validate
        config._config['llm']['openai_api_key'] = 'sk-test-key-1234567890abcdef'
        assert config.validate()

    def test_setup_script_exists(self):
        """Test that setup script exists and is executable."""
        assert os.path.exists('setup.py')

        # Test that setup script can be imported
        try:
            import setup
            assert hasattr(setup, 'main')
        except ImportError as e:
            pytest.fail(f"Setup script import failed: {e}")

    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        assert os.path.exists('requirements.txt')

        # Check that it contains expected packages
        with open('requirements.txt', 'r') as f:
            content = f.read()
            assert 'openai' in content
            assert 'flask' in content
            assert 'chromadb' in content

    def test_env_example_exists(self):
        """Test that .env.example exists."""
        assert os.path.exists('.env.example')

        # Check that it contains expected configuration
        with open('.env.example', 'r') as f:
            content = f.read()
            assert 'LLM_PROVIDER' in content
            assert 'OPENAI_API_KEY' in content
            assert 'SECRET_KEY' in content

    def test_directory_structure(self):
        """Test that required directories exist or can be created."""
        required_dirs = ['src', 'ui', 'tests', 'data', 'config', 'docs']

        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"Required directory {dir_name} does not exist"

    def test_readme_exists(self):
        """Test that README.md exists and contains expected content."""
        assert os.path.exists('README.md')

        # Use UTF-8 encoding to handle special characters
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Vynexa AI' in content
            assert 'GPT-5-like' in content
            assert 'Quick Start' in content
