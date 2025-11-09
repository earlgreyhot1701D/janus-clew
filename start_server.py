#!/usr/bin/env python3
"""Simple server startup script."""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.server import run_server

if __name__ == "__main__":
    run_server(host="127.0.0.1", port=3001)