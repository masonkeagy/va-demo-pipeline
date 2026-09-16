"""
Pytest configuration file.
Ensures the project root is in the Python path so test files
can import modules like 'read_data' correctly.
"""

import sys
from pathlib import Path

# Add the project root directory to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))