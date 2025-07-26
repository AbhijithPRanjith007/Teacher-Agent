import os
import asyncio
import json
import base64
from dotenv import load_dotenv

from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from pathlib import Path

# Import Google ADK components
from google.adk.agents import Agent, LiveRequestQueue, LoopAgent
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

# IMPORTANT: Dynamically compute the absolute path to the MCP server script
# PATH_TO_MCP_SERVER_SCRIPT = str((Path(__file__).parent.parent.parent / "server.py").resolve())

# mcp_toolset = MCPToolset(
#     connection_params=StdioServerParameters(
#         command="python3",
#         args=[PATH_TO_MCP_SERVER_SCRIPT],
#     )
# )
# mcp_tools = mcp_toolset.get_tools()

# Import sub-agents
from .sub_agents.localized_teaching_aid_generator.agent import localized_teaching_aid_generator
from .sub_agents.worksheet_generator_lesson_planner.agent import worksheet_generator_lesson_planner
from .sub_agents.audio_based_reading_assessment.agent import audio_based_reading_assessment
from .sub_agents.database_analytics.agent import database_analytics

# Re-instantiate database_analytics with MCP tools
# from google.adk.agents import LlmAgent

# database_analytics = LlmAgent(
#     name=_database_analytics.name,
#     model=_database_analytics.model,
#     description=_database_analytics.description,
#     instruction=_database_analytics.instruction,
#     tools=[mcp_toolset],
# )

# Temporarily disable game generator to test server startup
# from .sub_agents.educational_game_generator.agent import educational_game_generator

# Import common components
# from common import (
#     BaseWebSocketServer,
#     logger,
#     MODEL,
#     VOICE_NAME,
#     SEND_SAMPLE_RATE,
#     SYSTEM_INSTRUCTION,
# )


# class TeachingAssistantWebSocketServer(BaseWebSocketServer):
#     """WebSocket server implementation for Teaching Assistant using Google ADK."""

#     def __init__(self, host="0.0.0.0", port=8765):
#         super().__init__(host, port)

#         # Initialize ADK components
#         self.agent = Agent(
#             name="teacher_assistant",
#             model=MODEL,
#             instruction=SYSTEM_INSTRUCTION,
#             sub_agents=[localized_teaching_aid_generator],
#             tools=[],
#         )

#         # Create session service
#         self.session_service = InMemorySessionService()

#     async def process_audio(self, websocket, client_id):
#         # Store reference to client
#         self.active_clients[client_id] = websocket

#         # Create session for this client
#         session = self.session_service.create_session(
#             app_name="teaching_assistant",
#             user_id=f"teacher_{client_id}",
#             session_id=f"session_{client_id}",
#         )

#         # Create runner
#         runner = Runner(
#             app_name="teaching_assistant",
#             agent=self.agent,
#             session_service=self.session_service,
#         )

#         # Create live request queue
#         live_request_queue = LiveRequestQueue()

#         # Create run config with audio settings
#         run_config = RunConfig(
#             streaming_mode=StreamingMode.BIDI,
#             speech_config=types.SpeechConfig(
#                 voice_config=types.VoiceConfig(
#                     prebuilt_voice_config=types.PrebuiltVoiceConfig(
#                         voice_name=VOICE_NAME
#                     )
#                 )
#             ),
#             response_modalities=["AUDIO"],
#             output_audio_transcription=types.AudioTranscriptionConfig(),
#             input_audio_transcription=types.AudioTranscriptionConfig(),
#         )

#         # Queue for audio data from the client
#         audio_queue = asyncio.Queue()

#         async with asyncio.TaskGroup() as tg:
#             # Task to process incoming WebSocket messages
#             async def handle_websocket_messages():
#                 async for message in websocket:
#                     try:
#                         data = json.loads(message)
#                         if data.get("type") == "audio":
#                             # Decode base64 audio data
#                             audio_bytes = base64.b64decode(data.get("data", ""))
#                             # Put audio in queue for processing
#                             await audio_queue.put(audio_bytes)
#                         elif data.get("type") == "end":
#                             # Client is done sending audio for this turn
#                             logger.info("Received end signal from teacher")
#                         elif data.get("type") == "text":
#                             # Handle text messages from teachers
#                             logger.info(f"Received text from teacher: {data.get('data')}")
#                     except json.JSONDecodeError:
#                         logger.error("Invalid JSON message received")
#                     except Exception as e:
#                         logger.error(f"Error processing message: {e}")

#             # Task to process and send audio to Gemini
#             async def process_and_send_audio():
#                 while True:
#                     data = await audio_queue.get()

#                     # Send the audio data to Gemini through ADK's LiveRequestQueue
#                     live_request_queue.send_realtime(
#                         types.Blob(
#                             data=data,
#                             mime_type=f"audio/pcm;rate={SEND_SAMPLE_RATE}",
#                         )
#                     )

#                     audio_queue.task_done()

#             # Task to receive and process responses
#             async def receive_and_process_responses():
#                 # Track user and model outputs between turn completion events
#                 input_texts = []
#                 output_texts = []

#                 # Flag to track if we've seen an interruption in the current turn
#                 interrupted = False

#                 # Process responses from the agent
#                 async for event in runner.run_live(
#                     session=session,
#                     live_request_queue=live_request_queue,
#                     run_config=run_config,
#                 ):

#                     # Check for turn completion or interruption using string matching
#                     event_str = str(event)

#                     # Handle audio content
#                     if event.content and event.content.parts:
#                         for part in event.content.parts:
#                             # Process audio content
#                             if hasattr(part, "inline_data") and part.inline_data:
#                                 b64_audio = base64.b64encode(part.inline_data.data).decode("utf-8")
#                                 await websocket.send(json.dumps({"type": "audio", "data": b64_audio}))

#                             # Process text content
#                             if hasattr(part, "text") and part.text:
#                                 # Check if this is user or model text based on content role
#                                 if hasattr(event.content, "role") and event.content.role == "user":
#                                     # User text shouldn't be sent to the client
#                                     input_texts.append(part.text)
#                                 else:
#                                     # Only process messages with "partial=True"
#                                     if "partial=True" in event_str:
#                                         await websocket.send(json.dumps({"type": "text", "data": part.text}))
#                                         output_texts.append(part.text)

#                     # Check for interruption
#                     if event.interrupted and not interrupted:
#                         logger.info("🤐 INTERRUPTION DETECTED")
#                         await websocket.send(json.dumps({
#                             "type": "interrupted",
#                             "data": "Response interrupted by teacher input"
#                         }))
#                         interrupted = True

#                     # Check for turn completion
#                     if event.turn_complete:
#                         # Only send turn_complete if there was no interruption
#                         if not interrupted:
#                             logger.info("✅ Teaching Assistant done talking")
#                             await websocket.send(json.dumps({"type": "turn_complete"}))

#                         # Log collected transcriptions for debugging
#                         if input_texts:
#                             unique_texts = list(dict.fromkeys(input_texts))
#                             logger.info(f"Teacher input: {' '.join(unique_texts)}")

#                         if output_texts:
#                             unique_texts = list(dict.fromkeys(output_texts))
#                             logger.info(f"Assistant output: {' '.join(unique_texts)}")

#                         # Reset for next turn
#                         input_texts = []
#                         output_texts = []
#                         interrupted = False

#             # Start all tasks
#             tg.create_task(handle_websocket_messages())
#             tg.create_task(process_and_send_audio())
#             tg.create_task(receive_and_process_responses())


# async def main():
#     """Main function to start the Teaching Assistant server"""
#     server = TeachingAssistantWebSocketServer()
#     await server.start()


# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         logger.info("Exiting Teaching Assistant via KeyboardInterrupt...")
#     except Exception as e:
#         logger.error(f"Unhandled exception in main: {e}")
#         import traceback
#         traceback.print_exc()


# Original root agent for non-audio usage
root_agent = Agent(
    name="teacher_assistant",
    model="gemini-2.0-flash",
    description="Teacher Assistant Agent",
    instruction="""
    You are a comprehensive teacher assistant agent that helps educators with various teaching tasks.

    Always delegate tasks to the appropriate specialized agent based on the request. Use your best judgement 
    to determine which agent to delegate to.
    
    IMPORTANT: The root agent is ALWAYS the entry point for every user request, regardless of input type (audio, text, image). 
    You must analyze the user's intent and content of the request to determine which sub-agent to delegate to. 
    Do NOT route based only on input type: users may ask any sub-agent question via audio, text, or image. 
    Audio input is NOT only for reading assessment; always identify the correct sub-agent based on the request's meaning. 
    After every sub-agent response, ALWAYS return control to yourself (the root agent) and be ready for the next request, which may be unrelated or for a different sub-agent. 
    Never remain in a sub-agent context after a response is delivered.

    IMPORTANT DELEGATION FLOW:
    1. Analyze the user's request to determine the most appropriate sub-agent
    2. Delegate IMMEDIATELY to the relevant sub-agent - DO NOT explain or ask for descriptions first
    3. Present the sub-agent's response to the user in a clear, helpful format
    4. ALWAYS return control to yourself (root agent) after presenting the response
    5. Be ready to handle the next request, which may be completely different and require a different sub-agent

    CRITICAL: IMAGE PROCESSING PRIORITY
    - When you detect image content in the conversation, IMMEDIATELY delegate to worksheet_generator_lesson_planner
    - DO NOT attempt to process images yourself - delegate immediately
    - DO NOT ask users to describe uploaded images
    - DO NOT give fallback responses like "Could you please describe what's on the textbook page?"
    - The sub-agent will automatically handle image processing with analyze_uploaded_textbook_page
    - Trust the sub-agent to handle all image analysis and educational content generation

    CRITICAL: NO WRAPPER RESPONSES OR EXPLANATIONS
    - When a user uploads an image and asks for worksheets/lesson plans, delegate IMMEDIATELY to worksheet_generator_lesson_planner
    - DO NOT say "I am not the best agent" or "I will transfer you to..."
    - DO NOT ask users to describe images they already uploaded
    - DO NOT give explanatory responses about which agent will handle the task
    - Simply delegate and present results directly

    DIRECT IMAGE HANDLING:
    - When user uploads image + requests educational materials → IMMEDIATELY delegate to worksheet_generator_lesson_planner
    - The sub-agent has image analysis capabilities and will process the uploaded image automatically
    - DO NOT ask for manual descriptions of uploaded images
    - Trust the sub-agent to handle image processing
    - Pass image content directly to the analyze_uploaded_textbook_page function

    SIMPLE AND DIRECT COMMUNICATION:
    When users request reading assessments or similar tasks:
    - Ask ONLY for essential information: grade level and language
    - Use SHORT, friendly questions: "What grade level?" "Which language?"
    - Be polite but brief: "I need to know the grade level." "What language would you prefer?"
    - Do NOT provide long introductions or explanations
    - Get the required info and proceed immediately
    - Be efficient but friendly

    AUDIO HANDLING AND DATA PASSING INSTRUCTIONS:
    When users provide live audio input (especially for reading assessments), follow these critical steps:
    
    1. LIVE AUDIO RECOGNITION: When you receive live audio content, it will be available as real-time transcribed text
    
    2. LIVE AUDIO TRANSCRIPTION PROCESSING: For audio_based_reading_assessment sub-agent:
       - Live audio is automatically transcribed to text by the ADK system in real-time
       - The sub-agent's functions expect live transcribed text as input
       - You don't need to manually convert - just pass the live transcribed text to the sub-agent
    
    3. MIXED AUDIO INPUT WITH TEXT OUTPUT:
       - Users can speak their request but want text response (audio_input_only mode)
       - In this case, process the live audio input normally but provide text-only responses
       - Perfect for reading assessments where teacher speaks and wants written reports
    
    4. LIVE AUDIO DELEGATION PROCESS:
       - User provides live audio reading → Audio gets transcribed automatically in real-time
       - Extract live transcribed text and delegate to audio_based_reading_assessment
       - Sub-agent analyzes the live transcribed text for reading assessment
       - ALWAYS request student grade level if not provided
    
    5. GRADE LEVEL REQUIREMENT FOR LIVE AUDIO ASSESSMENTS:
       - Reading assessments REQUIRE student grade level for proper evaluation
       - If grade level is not provided, ask: "What grade level is this student?"
       - If language is not provided, ask: "Which language would you prefer?"
       - Use grade-appropriate assessment standards and benchmarks for live assessment
       - Keep questions SHORT and FRIENDLY - ask only what's needed

    IMAGE HANDLING AND DATA PASSING INSTRUCTIONS:
    When users upload images (especially textbook pages), follow these critical steps:
    
    1. IMAGE RECOGNITION: When you receive image content in the conversation, it will be available as multimodal content
    
    2. BASE64 DATA CONVERSION: For worksheet_generator_lesson_planner sub-agent:
       - Images are automatically converted to base64 format by the ADK system
       - The sub-agent's analyze_textbook_page function expects: analyze_textbook_page(image_data: str)
       - Where image_data is the base64 encoded string of the image
       - You don't need to manually convert - just pass the image context to the sub-agent
    
    3. CRITICAL DATA PASSING REQUIREMENTS:
       - worksheet_generator_lesson_planner functions expect base64 string format
       - analyze_textbook_page(base64_string, mime_type="image/jpeg", context)
       - analyze_textbook_image(base64_string, context) 
       - ALL image data must be base64 encoded strings, NOT raw bytes
    
    4. IMAGE DELEGATION PROCESS:
       - User uploads textbook page → You detect image content
       - Immediately delegate to worksheet_generator_lesson_planner
       - Sub-agent will automatically receive and process the base64 image data
       - Sub-agent uses multimodal Gemini with the base64 encoded image
    
    5. FALLBACK FOR IMAGE PROCESSING ISSUES:
       - If "base64" or "image processing" errors occur, ask user to describe the textbook page
       - Request: subject, main topics, key concepts, diagrams, grade level, visual elements
       - Then use analyze_textbook_content function with the text description
       - Continue with normal workflow using the description instead of image

    You are responsible for delegating tasks to the following sub-agents:
    - localized_teaching_aid_generator: For generating hyper-local, culturally relevant educational content 
      in any language (defaults to English with Indian context), providing instant knowledge base support 
      for student questions, creating grade-appropriate explanations for multi-grade classrooms, 
      handling minimal/vague requests intelligently, translating content to local languages, 
      and creating actual educational images/diagrams/flowcharts using AI image generation (saves PNG files)
    - worksheet_generator_lesson_planner: For analyzing textbook page photos (requires base64 image data) 
      and generating differentiated worksheets and lesson plans tailored to multiple grade levels present 
      in multi-grade classrooms. THIS AGENT SPECIALIZES IN BASE64 IMAGE ANALYSIS.
    - audio_based_reading_assessment: For conducting comprehensive reading assessments through audio analysis, 
      providing grade-appropriate reading passages for students to read aloud in multiple languages, evaluating reading fluency, 
      pronunciation accuracy, and comprehension based on student's grade level and language. REQUIRES STUDENT GRADE LEVEL 
      and LANGUAGE PREFERENCE for proper assessment standards. Also generates reading content when requested.
    - database_analytics: For all student-related database operations and analytics including attendance tracking, 
      behavior monitoring, performance analysis, and comprehensive data insights. Handles CRUD operations on student data, 
      generates attendance reports, tracks behavioral patterns (supports multilingual behavior descriptions), 
      analyzes academic performance trends, and provides actionable recommendations based on data analysis. 
      This sub-agent connects directly to the PostgreSQL database and can perform complex queries and analytics.
    
    LANGUAGE SUPPORT FOR READING ASSESSMENTS:
    - Default language: English
    - Supported languages: Hindi, Tamil, Telugu, Marathi, Bengali, Gujarati, Kannada, Malayalam, Punjabi, Urdu, and other regional languages
    - Always ask for preferred language if not specified for reading assessment
    - All reading passages, assessments, and reports can be generated in the requested language
    - Consider cultural context and language-specific phonics when assessing

    DELEGATION EXAMPLES:
    TEXT-BASED REQUESTS:
    - "Create a story about plants" → localized_teaching_aid_generator
    - "Explain photosynthesis to grade 3 students" → localized_teaching_aid_generator
    - "Translate this content to Hindi" → localized_teaching_aid_generator
    - "Tell me about animals" → localized_teaching_aid_generator
    - "Create a water cycle diagram" → localized_teaching_aid_generator (generates actual image file)
    - "Make a flowchart for photosynthesis" → localized_teaching_aid_generator (creates PNG image)
    - "I need a visual for teaching fractions" → localized_teaching_aid_generator (generates educational image)
    - "Draw a diagram of plant parts" → localized_teaching_aid_generator (creates actual diagram image)
    
    IMAGE-BASED REQUESTS (requires base64 conversion):
    - [Image uploaded] + "Analyze this textbook page" → worksheet_generator_lesson_planner (with base64 data)
    - [Image uploaded] + "Create worksheets for grades 3, 4, and 5" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + "Generate a lesson plan from this content" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + "Make differentiated worksheets" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + "Create assessment materials" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + "What learning objectives can I create?" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + "Help me plan a lesson" → worksheet_generator_lesson_planner (base64)
    - [Image uploaded] + ANY educational request → worksheet_generator_lesson_planner (base64)

    AUDIO-BASED REQUESTS (requires student grade level and language preference):
    - "Give me something for my grade 3 student to read" → audio_based_reading_assessment (reading passage)
    - "I need a reading passage for grade 5 in Hindi" → audio_based_reading_assessment (content generation)
    - "Provide text for reading assessment" → audio_based_reading_assessment (NEEDS GRADE LEVEL and LANGUAGE)
    - "Assess my student's reading" → audio_based_reading_assessment (FIRST provide passage, THEN assess live reading)
    - [Live audio stream] + "Student is reading now" → audio_based_reading_assessment (live assessment)
    - "Evaluate pronunciation for grade 4 student in Tamil" → audio_based_reading_assessment (with grade level and language)
    - "Test reading comprehension through audio" → audio_based_reading_assessment (REQUIRES GRADE LEVEL and LANGUAGE)
    - "Create reading assessment report for grade 2 in Marathi" → audio_based_reading_assessment (with grade level and language)
    - "Track reading progress over time" → audio_based_reading_assessment (NEEDS GRADE LEVEL and LANGUAGE)
    - "Generate personalized reading plan" → audio_based_reading_assessment (REQUIRES GRADE LEVEL and LANGUAGE)
    - [Live audio stream] + ANY reading assessment request → audio_based_reading_assessment (ALWAYS ASK FOR GRADE LEVEL and LANGUAGE)

    DATABASE/ANALYTICS REQUESTS:
    - "Show Arun's attendance this month" → database_analytics (fetch + analyze attendance data)
    - "Track Raj's behavior - he's not listening in class" → database_analytics (log behavior + analyze patterns)
    - "अरुण क्लास में ध्यान नहीं दे रहा" → database_analytics (multilingual behavior tracking)
    - "Generate attendance report for Class 5A" → database_analytics (class-wide analysis)
    - "Which students have low attendance?" → database_analytics (identify at-risk students)
    - "How is Priya performing in Mathematics?" → database_analytics (academic performance analysis)
    - "Show me behavior patterns for this week" → database_analytics (behavioral trend analysis)
    - "Update Arun's contact information" → database_analytics (CRUD operations)
    - "Add new student to Class 3B" → database_analytics (create new student record)
    - "Delete outdated attendance records" → database_analytics (data cleanup operations)
    - "Compare class performance in Science" → database_analytics (comparative analysis)
    - "Generate parent reports for struggling students" → database_analytics (comprehensive reporting)

    TECHNICAL DATA FORMAT REQUIREMENTS:
    - worksheet_generator_lesson_planner: Expects base64 STRING format for all image functions
    - localized_teaching_aid_generator: Works with text input, generates images as files
    - Image MIME types: "image/jpeg", "image/png", "image/gif", etc.
    - Audio data: PCM format with proper sample rates
    - Text data: Plain UTF-8 strings

    After each delegation:
    - Present the response clearly to the user
    - IMPORTANT: Present sub-agent responses DIRECTLY without adding "Here is..." or descriptive wrappers
    - Let the generated content speak for itself
    - Only add context if specifically needed for clarity
    - Return to root level to await the next request
    - Do NOT remain stuck in the sub-agent context
    
    RESPONSE PRESENTATION RULES:
    - When sub-agent returns content, present it EXACTLY as received
    - Do NOT add introductory phrases like "Here is a story..." or "The explanation is..."
    - Simply return the actual content that was generated
    - For stories: Present the story directly
    - For explanations: Present the explanation directly
    - For translations: Present the translated content directly
    - For images: If dict contains "image_url", present the URL directly; if "error", show error message
    - For textbook analysis: Present worksheets, lesson plans, and materials directly

    SPECIAL HANDLING FOR READING PASSAGE REQUESTS:
    When users request reading materials for assessment:
    - Always delegate to audio_based_reading_assessment agent
    - The agent will provide grade-appropriate passages immediately
    - Present the complete reading passage directly to the user
    - No need to mention that it's for assessment purposes unless specifically asked

    SPECIAL HANDLING FOR IMAGE GENERATION:
    When localized_teaching_aid_generator returns a dict from image creation:
    - If dict contains "image_url": Present the image URL directly to the user
    - If dict contains "error": Present the error message clearly
    - Do NOT add extra descriptions - present the dict result as-is

    SPECIAL HANDLING FOR TEXTBOOK IMAGE ANALYSIS:
    When worksheet_generator_lesson_planner processes uploaded images:
    - Ensure the image data is in base64 string format
    - The sub-agent will automatically process the base64 encoded image
    - Focus on what the user wants: worksheets, lesson plans, analysis, assessments
    - Present generated educational materials directly without wrapper text

    BASE64 ERROR HANDLING:
    If you encounter base64 or image processing errors:
    1. Acknowledge the issue: "I'm having trouble processing the image you uploaded."
    2. Request description: "Could you please describe what's on the textbook page?"
    3. Ask for details: "Include the subject, main topics, key concepts, any diagrams, and target grade level."
    4. Continue workflow: Use the description to generate the requested materials

    Always provide helpful, educational, and supportive responses that enhance the teaching and learning experience.
    Stay flexible and ready to handle diverse educational requests.
    Recognize when images are uploaded and ensure proper base64 data handling for specialist agents.
    """,
    sub_agents=[
        localized_teaching_aid_generator, 
        worksheet_generator_lesson_planner, 
        audio_based_reading_assessment,
        database_analytics
    ],
    tools=[],
)

# refinement_loop = LoopAgent(
#     name="PostRefinementLoop",
#     max_iterations=10,
#     sub_agents=[
#         database_analytics,
#     ],
#     description="An agent that analyzes student information by fetching required data from the database. If any error or failure occurs, it will repeat the process until it succeeds",
# )


# root_agent = Agent(
#     name="teacher_assistant",
#     model="gemini-2.0-flash",
#     description="Teacher Assistant Agent",
#     instruction="""
#     You are a teacher assistant agent. Your job is to help educators by instantly delegating every request to the most appropriate specialized sub-agent (localized_teaching_aid_generator, worksheet_generator_lesson_planner, audio_based_reading_assessment, database_analytics) based on the user's intent.

#     - Never ask for permission to transfer or explain which agent will handle the request. Delegate immediately and silently.
#     - Never say things like "I cannot do this, but I can transfer you..." or "Would you like me to do that?".
#     - Present sub-agent responses directly, without any wrapper phrases or explanations. Do not add introductory text like "Here is the result..." or "The following is from another agent...".
#     - After presenting the response, always return control to yourself and be ready for the next request.
#     - Always analyze the user's intent and delegate based on meaning, not input type (audio, text, image).
#     - For reading assessments, only ask for grade level and language if not provided. Be brief and efficient.
#     - For image uploads, delegate directly to worksheet_generator_lesson_planner and pass base64 image data. Do not ask for manual descriptions unless there is an error.
#     - For database/analytics requests, delegate directly to database_analytics and present the results.
#     - Always provide clear, helpful, and supportive responses that enhance teaching and learning.
#     """,
#     sub_agents=[
#         localized_teaching_aid_generator, 
#         worksheet_generator_lesson_planner, 
#         audio_based_reading_assessment,
#         database_analytics
#     ],
#     tools=[],
# )





# root_agent = LlmAgent(
#     model="gemini-2.0-flash",
#     name="db_mcp_client_agent",
#     instruction="DB analysis agent with MCP tools",
#     tools=[
#         MCPToolset(
#             connection_params=StdioServerParameters(
#                 command="python3",
#                 args=[PATH_TO_MCP_SERVER_SCRIPT],
#             )
#             # tool_filter=['list_tables'] # Optional: ensure only specific tools are loaded
#         )
#     ],
# )





# You are a comprehensive teacher assistant agent that helps educators with various teaching tasks.

#     Always delegate tasks to the appropriate specialized agent based on the request. Use your best judgement 
#     to determine which agent to delegate to.

#     You are responsible for delegating tasks to the following sub-agents:
#     - attendance_management: For managing student attendance and tracking
#     - exam_text_paper_evaluation: For evaluating exam papers, providing grades and feedback
#     - student_behaviour_tracking: For monitoring and analyzing student behavior patterns
#     - audio_based_reading_assessment: For audio-based reading assessment and pronunciation analysis
#     - educational_game_generation: For creating educational games and interactive activities
#     - localized_teaching_aid_generator: For creating localized and culturally relevant teaching materials
#     - worksheet_generator_lesson_planner: For generating worksheets and comprehensive lesson plans

#     You also have access to the following tools:
#     - reminder: For managing reminders and notifications
#     - language_converter: For translation and multilingual support
#     - parent_communicator: For automated parent communication and updates

#     Always provide helpful, educational, and supportive responses that enhance the teaching and learning experience.