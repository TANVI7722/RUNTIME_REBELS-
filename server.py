"""
Main Server Entrypoint.
Initializes SQLite database, mounts FastAPI endpoints and serves frontend static application.
"""

import os
import uvicorn
from fastapi.staticfiles import StaticFiles
from backend.database import init_db
from backend.api import app

# Initialize database schema and initial seed roster
init_db()

# Mount static frontend directory
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
os.makedirs(frontend_dir, exist_ok=True)
os.makedirs(os.path.join(frontend_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(frontend_dir, "js"), exist_ok=True)

# Mount frontend files
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    print("================================================================")
    print("  PHC EDGE AI - LOCAL INTELLIGENCE & OFFLINE RESILIENCE LAYER   ")
    print("  Server running at: http://localhost:8000                      ")
    print("  FastAPI Docs at:   http://localhost:8000/docs                 ")
    print("================================================================")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)
