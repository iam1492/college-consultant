
import os
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

from .upload_api import router as upload_router

# Initialize ADK-based FastAPI app
# Pointing to the directory containing agent folders (app/agents)
# ADK will scan this directory for folders (e.g., 'root_agent') containing 'agent.py'
AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")

# web=True to serve the ADK debug web interface and allow default handlers
app = get_fast_api_app(agents_dir=AGENTS_DIR, web=True, allow_origins=["*"])

# Include custom routers
app.include_router(upload_router)

@app.get("/")
async def root():
    return {"message": "College Consultant API is running"}

@app.on_event("startup")
async def startup_event():
    print("Registered Routes (Startup):")
    for route in app.routes:
        print(f"Path: {route.path} Name: {route.name}")

@app.get("/debug/routes")
async def debug_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else None
        })
    return routes
