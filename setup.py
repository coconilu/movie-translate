#!/usr/bin/env python3
"""
Setup script for Movie Translate
"""

import os
import sys
import json
import shutil
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        "resources/cache",
        "resources/temp",
        "output",
        "logs",
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def copy_config_template():
    """Copy configuration template"""
    source = "config.example.json"
    target = "config.json"
    
    if not Path(target).exists():
        shutil.copy2(source, target)
        print(f"✓ Created configuration file: {target}")
        print("  Please edit config.json to add your API keys")
    else:
        print(f"✓ Configuration file already exists: {target}")

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✓ Python version: {sys.version}")
    return True

def install_requirements():
    """Install requirements using uv"""
    try:
        import subprocess
        print("Installing requirements with uv...")
        
        # First check if uv is available
        try:
            subprocess.run(["uv", "--version"], check=True, capture_output=True)
            use_uv = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  uv not found, falling back to pip")
            use_uv = False
        
        if use_uv:
            result = subprocess.run(["uv", "pip", "install", "-r", "requirements.txt"], 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                                  capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Requirements installed successfully")
            return True
        else:
            print(f"❌ Failed to install requirements: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def main():
    """Main setup function"""
    print("Movie Translate Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    create_directories()
    
    # Copy config template
    copy_config_template()
    
    # Install requirements
    if not install_requirements():
        print("\n⚠️  Warning: Failed to install requirements automatically")
        print("Please run: uv pip install -r requirements.txt")
        print("Or fallback to: pip install -r requirements.txt")
    
    print("\n" + "=" * 50)
    print("Setup completed! 🎉")
    print("\nNext steps:")
    print("1. Edit config.json to add your API keys")
    print("2. Run the application: uv run python src/movie_translate/ui/main_app.py")
    print("3. For more information, see README.md")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())