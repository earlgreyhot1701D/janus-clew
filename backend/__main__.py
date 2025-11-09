"""Janus Clew Backend - Module entry point.

Allows running server as: python -m backend
"""

import logging
import sys
from .server import run_server  # Make sure run_server is defined in server.py

if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        logging.info("Server interrupted by user, shutting down.")
        sys.exit(0)
    except Exception:
        logging.exception("Unhandled exception while running server")
        sys.exit(1)
logging.basicConfig(level=logging.INFO)
