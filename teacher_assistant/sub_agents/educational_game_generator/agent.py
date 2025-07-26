from google.adk.agents import Agent
from .tools.simple_tools import create_simple_quiz_game, create_simple_math_game


# Create the educational game generator agent
educational_game_generator = Agent(
    name="educational_game_generator",
    model="gemini-2.0-flash",
    description="An agent that creates simple educational games.",
    instruction="""
    You are a simple educational game generator.
    
    When users request games, use the available tools:
    - create_simple_quiz_game: For quiz games about any topic
    - create_simple_math_game: For math practice games
    
    Always return the complete HTML game code from the tools.
    Keep responses focused on the game creation.
    """,
    tools=[create_simple_quiz_game, create_simple_math_game],
)