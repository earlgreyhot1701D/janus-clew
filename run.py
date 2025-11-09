#!/usr/bin/env python3
"""Simple server runner that bypasses config issues."""

import sys
import os
import uvicorn

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables directly
os.environ['API_PORT'] = '8000'
os.environ['AWS_BUILDER_ID_EMAIL'] = 'demo@example.com'

if __name__ == "__main__":
    print("Starting Janus Clew server on http://127.0.0.1:8000")
    print("Dashboard: http://127.0.0.1:8000")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(
        "backend.server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )