"""
Chat Router for College Consulting Service.

This router handles chat session management for the college agent.
"""

import uuid
import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/chat", tags=["chat"])

ADK_SERVER_URL = "http://localhost:8000"
APP_NAME = "college_agent"


@router.post("/session")
async def create_chat_session():
    """
    Create a new chat session for college consulting.
    
    This endpoint should be called when a user first enters the chat interface.
    It creates a new ADK session and returns the session_id for subsequent messages.
    
    Returns:
        dict: Contains session_id, user_id, and app_name for the new session.
    """
    session_id = str(uuid.uuid4())
    user_id = "user"  # Future: integrate with authentication
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create session via ADK API
            session_url = f"{ADK_SERVER_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
            
            response = await client.post(session_url, json={})
            response.raise_for_status()
            
            print(f"✅ Created new chat session: {session_id}")
            
    except httpx.HTTPStatusError as e:
        print(f"❌ Failed to create session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat session: {e.response.text}"
        )
    except Exception as e:
        print(f"❌ Error creating session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating chat session: {str(e)}"
        )
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "app_name": APP_NAME
    }


@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about an existing chat session.
    
    Args:
        session_id: The session ID to look up.
        
    Returns:
        dict: Session information from ADK.
    """
    user_id = "user"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            session_url = f"{ADK_SERVER_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
            
            response = await client.get(session_url)
            response.raise_for_status()
            
            return response.json()
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Session not found")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting session: {str(e)}"
        )
