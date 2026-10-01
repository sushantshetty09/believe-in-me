#!/usr/bin/env python3
"""
agent.py: Complete standalone local autonomous coding agent in a single file.
Can be executed directly via: python agent.py
"""
import sys
from pathlib import Path

# Insert package source directory into path so agent.py can run directly
src_dir = Path(__file__).parent / "src"
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from myagent.ui.cli import main

if __name__ == "__main__":
    main()
