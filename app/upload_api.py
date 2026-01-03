
import shutil
import os
import uuid
import httpx
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
import json

# Create router - will be mounted at /upload in main app usually, or we can add prefix here
router = APIRouter(tags=["upload"])

# Define paths: app/data/pdfs
# Current file: app/upload_api.py
# Base: app/
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
JSON_DIR = DATA_DIR / "json"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

ADK_SERVER_URL = "http://localhost:8000"

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename:
            return {"error": "No filename provided"}
            
        file_path = PDF_DIR / file.filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"File saved to {file_path}")
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        user_id = "admin" # Fixed user for now
        app_name = "root_agent" # According to agent.py
        
        # Invoke Agent via ADK API
        print(f"Invoking agent for {file.filename}...")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Debug: Check available apps
            try:
                apps_response = await client.get(f"{ADK_SERVER_URL}/list-apps")
                print(f"Available Apps: {apps_response.text}")
            except Exception as e:
                print(f"Failed to list apps: {e}")

            # Explicitly create session first
            session_url = f"{ADK_SERVER_URL}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            print(f"Creating session at {session_url}...")
            try:
                # create_session_with_id requires empty dict or valid session model if strict
                sess_response = await client.post(session_url, json={})
                sess_response.raise_for_status()
                print("Session created successfully.")
            except Exception as e:
                print(f"Failed to create session: {e}")
                # Try creating without ID if specific ID fails? No, run needs sessionId.
                # Just proceed and see if run works (maybe session exists)

            payload = {
                "appName": app_name,
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": f"Extract data from PDF: {file.filename}"}]
                }
            }
        
            # Switch to run_sse for streaming (standard ADK endpoint)
            events = []
            async with client.stream("POST", f"{ADK_SERVER_URL}/run_sse", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            # Filter out heartbeats or empty data if necessary, typically data is the event
                            events.append(data)
                        except json.JSONDecodeError:
                            print(f"Failed to decode SSE data: {line}")
            
            result = events
            
        print("Agent execution completed.")
        
        full_response_path = JSON_DIR / f"{file.filename}_full_response.json"
        with open(full_response_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return {
            "filename": file.filename,
            "message": "File uploaded and processed.",
            "saved_path": str(file_path),
            "agent_response_saved": str(full_response_path),
            "session_id": session_id
        }
            
    except Exception as e:
        print(f"Error processing upload: {e}")
        return {"error": str(e)}
