import os
from typing import Optional
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def create_quiz_game(topic: str, grade_level: str, questions_count: int, language: Optional[str]) -> str:
    """
    Create an interactive quiz game with HTML/CSS/JavaScript.
    
    Args:
        topic (str): The topic for the quiz
        grade_level (str): Student grade level
        questions_count (int): Number of questions to generate
        language (Optional[str]): Language for the quiz (defaults to English)
    
    Returns:
        str: Complete HTML game code
    """
    print(f"--- Tool: create_quiz_game called for {topic} ---")
    
    try:
        if not language:
            language = "English"
        if not questions_count:
            questions_count = 5
            
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple interactive quiz game in HTML with embedded CSS and JavaScript.
        
        Topic: {topic} for Grade {grade_level} in {language}
        Questions: {questions_count}
        
        Requirements:
        - Simple, clean design with bright colors
        - {questions_count} multiple choice questions about {topic}
        - Basic scoring (correct/total)
        - "Next" and "Restart" buttons
        - Congratulations message at end
        
        Generate a complete HTML file that works immediately in browser.
        Keep it simple and functional.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating quiz game: {str(e)}"


def create_math_game(operation: str, grade_level: str, difficulty: str, language: Optional[str]) -> str:
    """
    Create an interactive math practice game.
    
    Args:
        operation (str): Math operation (addition, subtraction, multiplication, division)
        grade_level (str): Student grade level
        difficulty (str): Difficulty level (easy, medium, hard)
        language (Optional[str]): Language for the game
    
    Returns:
        str: Complete HTML math game code
    """
    print(f"--- Tool: create_math_game called for {operation} ---")
    
    try:
        if not language:
            language = "English"
        if not difficulty:
            difficulty = "medium"
            
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple interactive math game in HTML with embedded CSS and JavaScript.
        
        Operation: {operation} for Grade {grade_level} 
        Difficulty: {difficulty}
        Language: {language}
        
        Requirements:
        - Simple math problems using {operation}
        - Basic scoring system
        - 10 questions total
        - "Next" and "Restart" buttons
        - Show correct answers when wrong
        
        Generate a complete HTML file that works immediately.
        Keep it simple and fast.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating math game: {str(e)}"


def create_memory_game(topic: str, grade_level: str, pairs_count: int, language: Optional[str]) -> str:
    """
    Create a memory matching game with educational content.
    
    Args:
        topic (str): Educational topic for the matching pairs
        grade_level (str): Student grade level
        pairs_count (int): Number of matching pairs
        language (Optional[str]): Language for the game
    
    Returns:
        str: Complete HTML memory game code
    """
    print(f"--- Tool: create_memory_game called for {topic} ---")
    
    try:
        if not language:
            language = "English"
        if not pairs_count:
            pairs_count = 8
            
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple memory matching game in HTML with embedded CSS and JavaScript.
        
        Topic: {topic} for Grade {grade_level} in {language}
        Pairs: {pairs_count}
        
        Requirements:
        - Simple card flip memory game
        - {pairs_count} pairs related to {topic}
        - Basic scoring by attempts
        - "Restart" button
        - Success message when complete
        
        Generate a complete HTML file that works immediately.
        Keep it simple and functional.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating memory game: {str(e)}"


def create_drag_drop_game(topic: str, grade_level: str, items_count: int, language: Optional[str]) -> str:
    """
    Create a drag and drop educational game.
    
    Args:
        topic (str): Educational topic for the drag-drop activity
        grade_level (str): Student grade level
        items_count (int): Number of items to drag and drop
        language (Optional[str]): Language for the game
    
    Returns:
        str: Complete HTML drag-drop game code
    """
    print(f"--- Tool: create_drag_drop_game called for {topic} ---")
    
    try:
        if not language:
            language = "English"
        if not items_count:
            items_count = 6
            
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple drag and drop game in HTML with embedded CSS and JavaScript.
        
        Topic: {topic} for Grade {grade_level} in {language}
        Items: {items_count}
        
        Requirements:
        - Simple drag and drop activity about {topic}
        - {items_count} items to drag and drop
        - Basic scoring system
        - Visual feedback for correct/wrong drops
        - "Restart" button
        
        Generate a complete HTML file that works immediately.
        Keep it simple and functional.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating drag-drop game: {str(e)}"


def create_word_puzzle(topic: str, grade_level: str, puzzle_type: str, language: Optional[str]) -> str:
    """
    Create word puzzles like word search, crossword, or anagram games.
    
    Args:
        topic (str): Educational topic for the words
        grade_level (str): Student grade level
        puzzle_type (str): Type of puzzle (word_search, crossword, anagram)
        language (Optional[str]): Language for the puzzle
    
    Returns:
        str: Complete HTML word puzzle game code
    """
    print(f"--- Tool: create_word_puzzle called for {puzzle_type} ---")
    
    try:
        if not language:
            language = "English"
        if not puzzle_type:
            puzzle_type = "word_search"
            
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple interactive {puzzle_type} game in HTML with embedded CSS and JavaScript.
        
        Topic: {topic} for Grade {grade_level} in {language}
        Puzzle Type: {puzzle_type}
        
        Requirements:
        - Simple {puzzle_type} with words about {topic}
        - Grade {grade_level} appropriate vocabulary
        - Basic word highlighting when found
        - Score tracking
        - "Restart" button
        
        Generate a complete HTML file that works immediately.
        Keep it simple and functional.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating word puzzle: {str(e)}"


def generate_game_ui(game_type: str, config: str) -> str:
    """
    Generate a complete game UI based on specifications.
    
    Args:
        game_type (str): Type of game to create
        config (str): JSON string of configuration parameters for the game
    
    Returns:
        str: Complete HTML game code
    """
    print(f"--- Tool: generate_game_ui called for {game_type} ---")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create a simple interactive educational game in HTML with embedded CSS and JavaScript.
        
        Game Type: {game_type}
        Configuration: {config}
        
        Requirements:
        - Simple, functional {game_type} game
        - Basic scoring and progress tracking
        - Clean, responsive design
        - "Restart" button
        
        Generate a complete HTML file that works immediately.
        Keep it simple and fast.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error generating game UI: {str(e)}"