# Teacher Assistant ADK

A powerful AI-powered teacher assistant built using Google's Agent Development Kit (ADK) that provides both HTTP and WebSocket APIs for text and audio-based interactions.

## Features

- **Multi-modal Conversations**: Support for text, audio, and image inputs
- **Real-time Communication**: WebSocket support for live audio streaming
- **HTTP API**: REST endpoints for integration with web applications
- **Session Management**: Persistent conversation context across interactions
- **Audio Capabilities**: Voice input/output with configurable modalities
- **Image Processing**: Support for image uploads and analysis
- **CORS Support**: Ready for cross-origin requests in production

## Architecture

The application uses Google's ADK framework with:
- **FastAPI** for HTTP endpoints and WebSocket connections
- **Google GenAI** for AI model interactions
- **In-memory session service** for conversation persistence
- **Dual model support**: Different models for HTTP vs WebSocket interactions

## Quick Setup

### Automated Setup (Recommended)

For Unix/Linux/macOS:
```bash
chmod +x setup.sh
./setup.sh
```

For Windows:
```cmd
setup.bat
```

### Manual Setup

### 1. Clone the repository:
```bash
git clone <repository-url>
cd agent-adk
```

### 2. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv teacher-assistant-env

# Activate virtual environment
# On Windows:
teacher-assistant-env\Scripts\activate
# On macOS/Linux:
source teacher-assistant-env/bin/activate
```

### 3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set up environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```bash
# Required: Add your Google AI API key
GOOGLE_API_KEY=your_actual_google_api_key_here

# Optional: Customize server settings
HOST=0.0.0.0
PORT=8000
```

### Required Environment Variables:
- `GOOGLE_API_KEY`: Your Google AI API key (Get from Google AI Studio)
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

### Getting Google AI API Key:
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

#### Health Check
```
GET /health
```
Returns server health status.

#### Chat API (HTTP)
```
POST /api/chat
Content-Type: application/json

{
  "message": "Your question here",
  "session_id": "optional-session-id",
  "image_data": "base64-encoded-image-data",
  "image_mime_type": "image/jpeg"
}
```

Response:
```json
{
  "response": "AI assistant response",
  "session_id": "session-identifier"
}
```

#### Session Management
```
DELETE /api/session/{session_id}  # Clear specific session
GET /api/sessions                 # List active sessions
```

#### WebSocket Connection
```
WS /ws/{session_id}?is_audio=true&audio_input_only=false
```

WebSocket message format:
```json
{
  "mime_type": "text/plain|audio/pcm|image/jpeg",
  "data": "message-content-or-base64-data",
  "role": "user"
}
```

### WebSocket Audio Configuration

- `is_audio=true`: Enable audio input/output
- `audio_input_only=true`: Audio input with text output
- `is_audio=false`: Text-only mode

## Project Structure

```
agent-adk/
├── main.py                 # Main FastAPI application
├── teacher_assistant/      # Agent configuration
│   └── agent.py           # Agent definition and models
├── static/                # Static web files (optional)
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Environment variables (create from .env.example)
├── setup.sh               # Unix/Linux setup script
├── setup.bat              # Windows setup script
└── README.md             # This file
```

## Key Components

### Session Management
- **HTTP Sessions**: Cached in memory with conversation context
- **WebSocket Sessions**: Managed with async context managers
- **Session State**: Maintains conversation history and user preferences

### Audio Processing
- **Input**: PCM audio data via WebSocket
- **Output**: Configurable text or audio responses
- **Voice**: Uses "Puck" voice configuration
- **Transcription**: Optional input/output audio transcription

### Error Handling
- Graceful WebSocket disconnection handling
- Async task cleanup and cancellation
- Comprehensive error logging

## Development

### Running in Development
```bash
# Install development dependencies
pip install uvicorn[standard]

# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Testing WebSocket Connection
Use a WebSocket client to connect to:
```
ws://localhost:8000/ws/test-session?is_audio=false
```

### Testing HTTP API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me with math?"}'
```

## Production Deployment

1. Set appropriate environment variables:
```bash
export HOST=0.0.0.0
export PORT=8000
```

2. Use a production ASGI server:
```bash
gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. Configure CORS origins for your domain:
```python
allow_origins=["https://yourdomain.com"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions, please [create an issue](link-to-issues) or contact the development team.
