#!/usr/bin/env python3
"""
Setup script for the AI Chatbot (GPT-5-like) project.
This script helps with project initialization and dependency installation.
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print("🐍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_virtual_environment():
    """Create a virtual environment."""
    if not os.path.exists('.venv'):
        return run_command('python -m venv .venv', 'Creating virtual environment')
    else:
        print("✅ Virtual environment already exists")
        return True


def activate_virtual_environment():
    """Provide instructions for activating virtual environment."""
    if os.name == 'nt':  # Windows
        activate_script = '.venv\\Scripts\\activate'
    else:  # Unix/Linux/Mac
        activate_script = '.venv/bin/activate'
    
    print(f"\n📝 To activate the virtual environment, run:")
    print(f"   {activate_script}")
    print()


def install_dependencies():
    """Install Python dependencies."""
    pip_command = 'python -m pip install --upgrade pip'
    requirements_command = 'pip install -r requirements.txt'
    
    success = run_command(pip_command, 'Upgrading pip')
    if success:
        success = run_command(requirements_command, 'Installing dependencies')
    
    return success


def create_directories():
    """Create necessary directories."""
    directories = ['data', 'logs', 'models']
    
    print("📁 Creating directories...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")


def setup_environment_file():
    """Set up the .env file from template."""
    env_example = '.env.example'
    env_file = '.env'
    
    if os.path.exists(env_example) and not os.path.exists(env_file):
        shutil.copy2(env_example, env_file)
        print(f"✅ Created {env_file} from template")
        print(f"📝 Please edit {env_file} and add your API keys")
    elif os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
    else:
        print(f"❌ {env_example} not found")


def main():
    """Main setup function."""
    print("🚀 Setting up AI Chatbot (GPT-5-like) project...\n")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Provide activation instructions
    activate_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed. Please check your environment and try again.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment file
    setup_environment_file()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment")
    print("2. Edit the .env file and add your API keys")
    print("3. Run the CLI: python ui/cli/main.py chat -m 'Hello!'")
    print("4. Or start the web interface: python ui/web/app.py")
    print("\n📖 See README.md for detailed usage instructions.")


if __name__ == '__main__':
    main()
