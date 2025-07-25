# import asyncio
# import json
# import base64
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Import Google Generative AI components
# from google import genai
# from google.genai import types
# from google.genai.types import (
#     LiveConnectConfig,
#     SpeechConfig,
#     VoiceConfig,
#     PrebuiltVoiceConfig,
# )

# # Import common components
# from common import (
#     BaseWebSocketServer,
#     logger,
#     PROJECT_ID,
#     LOCATION,
#     MODEL,
#     VOICE_NAME,
#     SEND_SAMPLE_RATE,
#     SYSTEM_INSTRUCTION,
# )

# # Get Google API key from environment
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# # Initialize Google client
# client = genai.Client(api_key=GOOGLE_API_KEY)

# # LiveAPI Configuration for Teaching Assistant
# config = LiveConnectConfig(
#     response_modalities=["AUDIO"],
#     output_audio_transcription={},
#     input_audio_transcription={},
#     speech_config=SpeechConfig(
#         voice_config=VoiceConfig(
#             prebuilt_voice_config=PrebuiltVoiceConfig(voice_name=VOICE_NAME)
#         )
#     ),
#     session_resumption=types.SessionResumptionConfig(handle=None),
#     system_instruction=SYSTEM_INSTRUCTION,
# )

# class TeachingAssistantLiveAPIServer(BaseWebSocketServer):
#     """WebSocket server implementation for Teaching Assistant using Gemini LiveAPI directly."""

#     async def process_audio(self, websocket, client_id):
#         # Store reference to teacher
#         self.active_clients[client_id] = websocket

#         # Connect to Gemini using LiveAPI
#         async with client.aio.live.connect(model=MODEL, config=config) as session:
#             async with asyncio.TaskGroup() as tg:
#                 # Create a queue for audio data from the teacher
#                 audio_queue = asyncio.Queue()

#                 # Task to process incoming WebSocket messages
#                 async def handle_websocket_messages():
#                     async for message in websocket:
#                         try:
#                             data = json.loads(message)
#                             if data.get("type") == "audio":
#                                 # Decode base64 audio data
#                                 audio_bytes = base64.b64decode(data.get("data", ""))
#                                 # Put audio in queue for processing
#                                 await audio_queue.put(audio_bytes)
#                             elif data.get("type") == "end":
#                                 # Teacher is done sending audio for this turn
#                                 logger.info("Received end signal from teacher")
#                             elif data.get("type") == "text":
#                                 # Handle text messages from teachers
#                                 logger.info(f"Received text from teacher: {data.get('data')}")
#                         except json.JSONDecodeError:
#                             logger.error("Invalid JSON message received")
#                         except Exception as e:
#                             logger.error(f"Error processing message: {e}")

#                 # Task to process and send audio to Gemini
#                 async def process_and_send_audio():
#                     while True:
#                         data = await audio_queue.get()

#                         # Send the audio data to Gemini
#                         await session.send_realtime_input(
#                             media={
#                                 "data": data,
#                                 "mime_type": f"audio/pcm;rate={SEND_SAMPLE_RATE}",
#                             }
#                         )

#                         audio_queue.task_done()

#                 # Task to receive and process teaching assistant responses
#                 async def receive_and_respond():
#                     while True:
#                         teacher_input_transcriptions = []
#                         assistant_output_transcriptions = []

#                         async for response in session.receive():
#                             # Get session resumption update if available
#                             if response.session_resumption_update:
#                                 update = response.session_resumption_update
#                                 if update.resumable and update.new_handle:
#                                     session_id = update.new_handle
#                                     logger.info(f"New Teaching Session: {session_id}")
#                                     # Send session ID to teacher
#                                     session_id_msg = json.dumps({
#                                         "type": "session_id",
#                                         "data": session_id,
#                                         "message": "Teaching session started"
#                                     })
#                                     await websocket.send(session_id_msg)

#                             # Check if connection will be terminated soon
#                             if response.go_away is not None:
#                                 logger.info(f"Teaching session will terminate in: {response.go_away.time_left}")

#                             server_content = response.server_content

#                             # Handle interruption
#                             if (hasattr(server_content, "interrupted") and server_content.interrupted):
#                                 logger.info("🤐 TEACHER INTERRUPTION DETECTED")
#                                 # Notify the teacher
#                                 await websocket.send(json.dumps({
#                                     "type": "interrupted",
#                                     "data": "Response interrupted by teacher input"
#                                 }))

#                             # Process teaching assistant response
#                             if server_content and server_content.model_turn:
#                                 for part in server_content.model_turn.parts:
#                                     if part.inline_data:
#                                         # Send audio response to teacher
#                                         b64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
#                                         await websocket.send(json.dumps({
#                                             "type": "audio",
#                                             "data": b64_audio
#                                         }))

#                             # Handle turn completion
#                             if server_content and server_content.turn_complete:
#                                 logger.info("✅ Teaching Assistant done responding")
#                                 await websocket.send(json.dumps({
#                                     "type": "turn_complete",
#                                     "message": "Teaching Assistant response complete"
#                                 }))

#                             # Handle transcriptions
#                             output_transcription = getattr(response.server_content, "output_transcription", None)
#                             if output_transcription and output_transcription.text:
#                                 assistant_output_transcriptions.append(output_transcription.text)
#                                 # Send assistant text to teacher
#                                 await websocket.send(json.dumps({
#                                     "type": "text",
#                                     "data": output_transcription.text
#                                 }))

#                             input_transcription = getattr(response.server_content, "input_transcription", None)
#                             if input_transcription and input_transcription.text:
#                                 teacher_input_transcriptions.append(input_transcription.text)

#                         logger.info(f"Assistant output: {''.join(assistant_output_transcriptions)}")
#                         logger.info(f"Teacher input: {''.join(teacher_input_transcriptions)}")

#                 # Start all tasks
#                 tg.create_task(handle_websocket_messages())
#                 tg.create_task(process_and_send_audio())
#                 tg.create_task(receive_and_respond())

# async def main():
#     """Main function to start the Teaching Assistant server"""
#     server = TeachingAssistantLiveAPIServer()
#     await server.start()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Exiting Teaching Assistant server via KeyboardInterrupt...")
#     except Exception as e:
#         logger.error(f"Unhandled exception in Teaching Assistant server: {e}")
#         import traceback
#         traceback.print_exc()