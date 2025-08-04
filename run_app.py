#!/usr/bin/env python3
"""
Movie Translate Application Entry Point
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from movie_translate.ui.main_app import main

if __name__ == "__main__":
    main()