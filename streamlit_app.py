import os
import sys

# Ensure the project root is in python search path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add the 'frontend' directory to resolve its internal modules (like utils)
frontend_dir = os.path.join(project_root, "frontend")
if frontend_dir not in sys.path:
    sys.path.insert(0, frontend_dir)

# Import the main frontend UI module (renamed from app to avoid namespace collisions)
import streamlit_ui
