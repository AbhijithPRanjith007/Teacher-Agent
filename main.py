import asyncio
import base64
import json
import os
import uvicorn
import uuid
from pathlib import Path
from typing import AsyncIterable

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from teacher_assistant.agent import root_agent, HTTP_MODEL, WEBSOCKET_MODEL


# Load environment variables
load_dotenv()

APP_NAME = "Teacher Assistant ADK Production"
session_service = InMemorySessionService()

# Session cache for HTTP requests (stores session metadata)
http_session_cache = {}

app = FastAPI(title="Teacher Assistant API", version="1.0.0")

# Add CORS middleware for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with your specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path("static")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


async def start_agent_session(session_id, is_audio=False, audio_input_only=False):
    """Starts an agent session"""
    # Create a Session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality based on audio_input_only flag
    if is_audio and not audio_input_only:
        modality = "AUDIO"
    else:
        modality = "TEXT"

    # Create speech config with voice settings
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )

    # Create run config with basic settings
    config = {"response_modalities": [modality], "speech_config": speech_config}

    # Add input audio transcription when any audio input is enabled
    if is_audio or audio_input_only:
        config["input_audio_transcription"] = {}
    
    if is_audio and not audio_input_only:
        config["output_audio_transcription"] = {}

    run_config = RunConfig(**config)

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(
    websocket: WebSocket, live_events: AsyncIterable[Event | None]
):
    """Agent to client communication"""
    while True:
        async for event in live_events:
            if event is None:
                continue

            # If the turn complete or interrupted, send it
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: {message}")
                continue

            # Read the Content and its first Part
            part = event.content and event.content.parts and event.content.parts[0]
            if not part:
                continue

            # Make sure we have a valid Part
            if not isinstance(part, types.Part):
                continue

            # Only send text if it's a partial response (streaming)
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text,
                    "role": "model",
                }
                await websocket.send_text(json.dumps(message))
                print(f"[AGENT TO CLIENT]: text/plain: {part.text}")

            # If it's audio, send Base64 encoded audio data
            is_audio = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("audio/pcm")
            )
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii"),
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")

            # If it's an image, send Base64 encoded image data
            is_image = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("image/")
            )
            if is_image:
                image_data = part.inline_data and part.inline_data.data
                if image_data:
                    message = {
                        "mime_type": part.inline_data.mime_type,
                        "data": base64.b64encode(image_data).decode("ascii"),
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: {part.inline_data.mime_type}: {len(image_data)} bytes.")


async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]
        role = message.get("role", "user")

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = types.Content(role=role, parts=[types.Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send audio data
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
        elif mime_type.startswith("image/"):
            # Handle image data (JPEG, PNG, etc.)
            decoded_data = base64.b64decode(data)
            
            # Create image part and send as content
            image_part = types.Part(
                inline_data=types.Blob(data=decoded_data, mime_type=mime_type)
            )
            content = types.Content(role=role, parts=[image_part])
            live_request_queue.send_content(content=content)
            print(f"[CLIENT TO AGENT]: {mime_type}: {len(decoded_data)} bytes")
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


# HTTP endpoint for Flask backend integration
@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """HTTP endpoint for text-based chat integration with Flask backend"""
    try:
        message = request.get("message", "")
        session_id = request.get("session_id", str(uuid.uuid4()))
        image_data = request.get("image_data")  # Base64 encoded image
        image_mime_type = request.get("image_mime_type", "image/jpeg")
        
        if not message and not image_data:
            raise HTTPException(status_code=400, detail="Message or image is required")
        
        # Check if session exists in cache
        if session_id not in http_session_cache:
            # Initial state for new sessions
            initial_state = {
                "conversation_context": [],
                "user_preferences": "Educational content creator",
                "session_type": "http_chat"
            }
            
            # Create new session with state
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=f"user_{session_id}",
                session_id=session_id,
                state=initial_state,
            )
            
            # Create runner for this session
            runner = Runner(
                agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service,
            )
            
            # Cache the session components
            http_session_cache[session_id] = {
                'session': session,
                'runner': runner,
                'user_id': f"user_{session_id}",
            }
            
            print(f"Created new session: {session_id}")
        
        # Get cached session components
        cached_session = http_session_cache[session_id]
        runner = cached_session['runner']
        user_id = cached_session['user_id']
        
        # Prepare content parts
        parts = []
        
        # Add text if provided
        if message:
            parts.append(types.Part.from_text(text=message))
        
        # Add image if provided
        if image_data:
            try:
                decoded_image = base64.b64decode(image_data)
                image_part = types.Part(
                    inline_data=types.Blob(data=decoded_image, mime_type=image_mime_type)
                )
                parts.append(image_part)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
        
        # Create the user message
        new_message = types.Content(role="user", parts=parts)
        
        # Run the agent with proper session handling
        response_text = ""
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                    break
        
        # Update session state with conversation context
        session = await session_service.get_session(
            app_name=APP_NAME, 
            user_id=user_id, 
            session_id=session_id
        )
        
        # Add to conversation context if session exists
        if session and hasattr(session, 'state') and session.state:
            if "conversation_context" not in session.state:
                session.state["conversation_context"] = []
            
            session.state["conversation_context"].append({
                "user_message": message,
                "agent_response": response_text
            })
        
        return {"response": response_text, "session_id": session_id}
        
    except Exception as e:
        print(f"Error in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Add session management endpoints
@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a specific session from cache"""
    if session_id in http_session_cache:
        del http_session_cache[session_id]
        return {"message": f"Session {session_id} cleared"}
    return {"message": f"Session {session_id} not found"}


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions (for debugging)"""
    return {"active_sessions": list(http_session_cache.keys())}


# WebSocket endpoint for real-time communication
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query(...),
    audio_input_only: str = Query(default="false"),
):
    """WebSocket endpoint for real-time audio communication"""
    await websocket.accept()
    audio_input_only_bool = audio_input_only.lower() == "true"
    print(f"Client #{session_id} connected, audio mode: {is_audio}, audio input only: {audio_input_only_bool}")
    
    live_events, live_request_queue = await start_agent_session(
        session_id, is_audio == "true", audio_input_only_bool
    )
    
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)
    
    print(f"Client #{session_id} disconnected")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    return {"status": "healthy", "app": APP_NAME}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
    return {"message": "Teacher Assistant API is running", "endpoints": ["/api/chat", "/ws/{session_id}", "/health"]}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)