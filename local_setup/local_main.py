"""
Modified main.py for Local Environment
--------------------------------------
This is a modified version of main.py for running the application locally.
It uses localhost instead of 0.0.0.0 to ensure the application runs properly
on a local development environment.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app


if __name__ == "__main__":
    # Set host to 'localhost' for local-only access, or '0.0.0.0' for network-wide access
    app.run(host='localhost', port=5000, debug=True)