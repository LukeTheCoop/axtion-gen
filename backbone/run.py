#!/usr/bin/env python3
import os
import sys
import uvicorn

# Add the current directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # Run the FastAPI app with uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 