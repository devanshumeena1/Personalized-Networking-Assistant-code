import os
import sys

# Ensure project root is in python search path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Read and execute frontend/app.py in-process
frontend_dir = os.path.join(project_root, "frontend")
app_path = os.path.join(frontend_dir, "app.py")
with open(app_path, "r", encoding="utf-8") as f:
    code = f.read()

# Execute the code in the global namespace
exec(code, globals())
