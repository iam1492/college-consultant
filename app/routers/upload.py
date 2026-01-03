
import shutil
import os
import uuid
import httpx
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
import json

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={404: {"description": "Not found"}},
)

# Define paths: app/data/pdfs
# Current file: app/routers/upload.py
# Base: app/
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
JSON_DIR = DATA_DIR / "json"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)

ADK_SERVER_URL = "http://localhost:8000"

@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename:
            return {"error": "No filename provided"}
            
        file_path = PDF_DIR / file.filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"File saved to {file_path}")
        
        # Generate a session ID (or use a fixed one for MVP testing if preferred, but UUID is better)
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

            payload = {
                "appName": app_name,
                "userId": user_id,
                "sessionId": session_id,
                "newMessage": {
                    "role": "user",
                    "parts": [{"text": f"Extract data from PDF: {file.filename}"}]
                }
            }
        
            response = await client.post(f"{ADK_SERVER_URL}/run", json=payload)
            response.raise_for_status()
            result = response.json()
            
        print("Agent execution completed.")
        
        # Attempt to find the JSON output in the events or check if file was created
        # The agent instructions say "Extract... and save JSON" (implied by schema output or tool?) 
        # Wait, the agent has an output_schema. The result of the run will contain the model's final response which should conform to the schema.
        # We need to save this structured output to data/json/{filename}.json
        
        # ADK /run response format is a list of events. We need to find the model response.
        # Typically the last event or "ModelResponse" event.
        # Let's inspect the documented response format or assume standard ADK event structure.
        # For simplicity, if the agent returns the JSON object as its final answer, we can capture it.
        
        # Since we defined output_schema in the agent, the ADK might wrap the output.
        # Let's save the raw result for inspection and try to extract the data.
        
        # For MVP, let's assume the agent just returns the text/json and we save what we get.
        # Or better, if the agent successfully used the schema, the last message part text should be the JSON.
        
        # Simplest approach: Save the whole result for debugging, and if we can parse the JSON, save that too.
        json_output_path = JSON_DIR / f"{file.filename}.json"
        
        # Try to extract the structured data from the response events
        # This part depends heavily on ADK's response structure for structured output.
        # We'll save the raw API response first.
        
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
