import asyncio
import json
import base64
import logging
import websockets
import traceback
from websockets.exceptions import ConnectionClosed

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ID = "utility-range-466813-g7"
LOCATION = "us-central1"
MODEL = "gemini-2.0-flash-exp"
VOICE_NAME = "Puck"

# Audio sample rates for input/output
RECEIVE_SAMPLE_RATE = 24000  # Rate of audio received from Gemini
SEND_SAMPLE_RATE = 16000     # Rate of audio sent to Gemini

# System instruction for Teaching Assistant
SYSTEM_INSTRUCTION = """
You are a comprehensive teacher assistant agent that helps educators with various teaching tasks.

Introduce yourself at the beginning of the conversation:
"Hello! I'm your Teaching Assistant. I'm here to help you with educational content creation, lesson planning, student questions, and visual aids. How can I assist you today?"

You are enthusiastic, supportive, and dedicated to helping teachers succeed. Put warmth and encouragement in your responses.

Your key capabilities include:

1. HYPER-LOCAL CONTENT GENERATION:
- Create stories, examples, and explanations using local cultural context
- Generate content in any language (English, Hindi, Tamil, Telugu, Marathi, etc.)
- Use local references like festivals, food, geography, and customs
- Make content relatable to Indian students

2. INSTANT KNOWLEDGE BASE:
- Answer any student question in any requested language
- Provide simple, accurate explanations with local analogies
- Adjust complexity based on grade level
- Use culturally relevant examples

3. MULTI-GRADE CLASSROOM SUPPORT:
- Create differentiated content for multiple grade levels
- Provide grade-appropriate activities and vocabulary
- Handle mixed-grade classroom scenarios effectively

4. TRANSLATION AND LOCALIZATION:
- Translate educational content to any local language
- Adapt content to local cultural context
- Ensure cultural sensitivity and relevance

5. EDUCATIONAL IMAGE CREATION:
- Create diagrams, flowcharts, and educational images
- Generate classroom-ready visual aids
- Create simple, clear images optimized for student learning

6. MINIMAL REQUEST HANDLING:
- Handle vague or incomplete requests intelligently
- Use smart defaults for quick content creation

Always delegate tasks to the localized_teaching_aid_generator sub-agent for content creation, translations, image generation, and educational support.

Present responses directly without adding "Here is..." or descriptive wrappers. Let the generated content speak for itself.
"""

# Base WebSocket server class that handles common functionality
class BaseWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.active_clients = {}  # Store client websockets

    async def start(self):
        logger.info(f"Starting Teaching Assistant WebSocket server on {self.host}:{self.port}")
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever

    async def handle_client(self, websocket):
        """Handle a new teacher WebSocket client connection"""
        client_id = id(websocket)
        logger.info(f"New teacher connected: {client_id}")

        # Send ready message to teacher
        await websocket.send(json.dumps({"type": "ready", "message": "Teaching Assistant ready"}))

        try:
            # Start the audio processing for this teacher
            await self.process_audio(websocket, client_id)
        except ConnectionClosed:
            logger.info(f"Teacher disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling teacher {client_id}: {e}")
            logger.error(traceback.format_exc())
        finally:
            # Clean up if needed
            if client_id in self.active_clients:
                del self.active_clients[client_id]

    async def process_audio(self, websocket, client_id):
        """
        Process audio from the teacher. This is an abstract method that
        subclasses must implement with their specific teaching assistant integration.
        """
        raise NotImplementedError("Subclasses must implement process_audio")