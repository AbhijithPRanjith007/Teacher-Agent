import os
from datetime import datetime
from typing import List, Optional
import google.generativeai as genai
from google import genai as google_genai
from google.genai import types
from PIL import Image
from io import BytesIO
import requests
from pathlib import Path
from google.cloud import storage
import uuid

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_hyper_local_content(topic: str, local_language: Optional[str] = None, cultural_context: Optional[str] = None, content_type: Optional[str] = None) -> str:
    """
    Generate culturally relevant educational content in local language using Gemini AI.
    
    Creates stories, explanations, or other educational content that incorporates local cultural 
    references, festivals, food, customs, and context to make learning more relatable for students.
    
    Args:
        topic (str): The educational topic or subject to create content about (required)
        local_language (Optional[str]): Target language for content (defaults to English if None)
        cultural_context (Optional[str]): Cultural context to incorporate (defaults to Indian if None)
        content_type (Optional[str]): Type of content to create - story, explanation, example, etc. (defaults to story if None)
    
    Returns:
        str: Generated educational content in the specified language and cultural context
        
    Examples:
        generate_hyper_local_content("water cycle", "Hindi", "Rajasthani", "story")
        generate_hyper_local_content("photosynthesis", None, None, "explanation")
    """
    print(f"--- Tool: generate_hyper_local_content called for {topic} ---")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set intelligent defaults if parameters are not provided
        if not local_language:
            local_language = "English"  # Default to English
        
        if not cultural_context:
            cultural_context = "Indian"  # Default to general Indian context
            
        if not content_type:
            content_type = "story"  # Default to story
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Craft prompt for hyper-local content generation
        prompt = f"""
        Create a {content_type} about {topic} in {local_language} language using {cultural_context} cultural context.
        
        Requirements:
        - Write primarily in {local_language} language (if not specified, use English with some local terms)
        - Include local cultural references like festivals, food, places, customs from {cultural_context} culture
        - Make it educational and engaging for school students
        - Use simple, age-appropriate language
        - If cultural context is not specific, use general Indian cultural elements
        - Make the content relatable to Indian students
        
        Topic: {topic}
        Content Type: {content_type}
        Language: {local_language}
        Cultural Context: {cultural_context}
        
        Please provide a complete {content_type} that students can easily relate to and understand.
        If any information is missing, use your best judgment to create appropriate content.
        """
        
        response = model.generate_content(prompt)
        generated_content = response.text
        
        return generated_content
        
    except Exception as e:
        return f"Error generating content: {str(e)}"


def provide_knowledge_base_answer(question: str, language: Optional[str] = None, grade_level: Optional[str] = None) -> str:
    """
    Provide simple, accurate explanations for student questions in specified language using Gemini AI.
    
    Answers educational questions with appropriate complexity based on grade level and cultural context.
    Uses local analogies and examples to make explanations more relatable for Indian students.
    
    Args:
        question (str): The student question to answer (required)
        language (Optional[str]): Language for the answer (defaults to English if None)
        grade_level (Optional[str]): Student grade level to adjust complexity (defaults to general level if None)
    
    Returns:
        str: Educational answer with appropriate complexity and cultural context
        
    Examples:
        provide_knowledge_base_answer("Why is the sky blue?", "Hindi", "3")
        provide_knowledge_base_answer("Explain photosynthesis", None, "8")
    """
    print(f"--- Tool: provide_knowledge_base_answer called for question: {question} ---")
    
    try:
        # Set intelligent defaults if parameters are not provided
        if not language:
            language = "English"  # Default to English
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Determine explanation complexity based on grade level
        if grade_level and grade_level.isdigit() and int(grade_level) <= 3:
            complexity = "very simple, using basic words and concepts"
        elif grade_level and grade_level.isdigit() and int(grade_level) <= 6:
            complexity = "simple to intermediate, with some educational terms"
        elif grade_level and grade_level.isdigit():
            complexity = "detailed with proper scientific/academic terminology"
        else:
            complexity = "general level appropriate for school students"
        
        # Craft prompt for knowledge base answer
        prompt = f"""
        Answer this student question: "{question}"
        
        Requirements:
        - Provide answer in {language} language (if English/local mix is needed, that's fine)
        - Use {complexity} explanation level
        - Include local cultural analogies and examples that students in India can relate to
        - Make it educational and accurate
        - Use examples from daily life, nature, or local context
        - If grade level is specified, make it appropriate for grade {grade_level if grade_level else 'general'}
        - If language is not specified, use simple English with local terms where needed
        
        Question: {question}
        Language: {language}
        Grade Level: {grade_level if grade_level else 'Not specified - use general level'}
        
        Please provide a clear, accurate, and culturally relevant explanation.
        Use your best judgment for any missing information.
        """
        
        response = model.generate_content(prompt)
        answer = response.text
        
        return answer
        
    except Exception as e:
        return f"Error providing answer: {str(e)}"


def answer_question(question: str) -> str:
    """
    Simple wrapper for answering questions with default settings.
    
    Provides a simplified interface for basic question answering using English language 
    and general grade level. This wrapper calls provide_knowledge_base_answer with defaults.
    
    Args:
        question (str): The student question to answer
    
    Returns:
        str: Educational answer in English with general complexity level
        
    Examples:
        answer_question("Why is the sky blue?")
        answer_question("How do plants grow?")
    """
    return provide_knowledge_base_answer(question, None, None)


def create_multi_grade_content(topic: str, grade_levels: List[str], language: Optional[str] = None, subject: Optional[str] = None) -> dict:
    """
    Create grade-appropriate educational content for multi-grade classrooms using Gemini AI.
    
    Generates differentiated educational content suitable for multiple grade levels simultaneously.
    Each grade level receives content with appropriate complexity, activities, and vocabulary.
    
    Args:
        topic (str): The educational topic to create content about (required)
        grade_levels (List[str]): List of grade levels to create content for (required)
        language (Optional[str]): Language for content (defaults to English if None)
        subject (Optional[str]): Subject area (defaults to General Studies if None)
    
    Returns:
        dict: Structured content organized by grade level with explanations, activities, and metadata
        
    Examples:
        create_multi_grade_content("photosynthesis", ["3", "5", "7"], "English", "Science")
        create_multi_grade_content("water cycle", ["2", "4"], None, None)
    """
    print(f"--- Tool: create_multi_grade_content called for grades: {grade_levels} ---")
    
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Set intelligent defaults if parameters are not provided
        if not language:
            language = "English"  # Default to English for Indian context
        
        if not subject:
            subject = "General Studies"  # Default subject if not specified
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        content_by_grade = {}
        
        for grade in grade_levels:
            # Determine appropriate complexity and activities for each grade
            if int(grade) <= 3:
                complexity = "very simple with pictures and basic concepts"
                activities = "drawing, coloring, simple games, storytelling"
                vocabulary_level = "basic everyday words"
            elif int(grade) <= 6:
                complexity = "intermediate with some detailed explanations"
                activities = "group discussions, hands-on experiments, role-playing"
                vocabulary_level = "intermediate terms with explanations"
            else:
                complexity = "advanced with detailed scientific/academic concepts"
                activities = "research projects, critical analysis, presentations"
                vocabulary_level = "advanced terminology and concepts"
            
            # Craft prompt for each grade level
            prompt = f"""
            Create educational content about {topic} in {language} for grade {grade} students studying {subject}.
            
            Requirements:
            - Write in {language} language (mix with English if needed)
            - Use {complexity}
            - Include cultural references relevant to Indian students
            - Provide grade-appropriate explanation
            - Suggest {activities} as learning activities
            - Include {vocabulary_level} vocabulary list
            - If subject is not specific, create general educational content
            
            Topic: {topic}
            Subject: {subject}
            Grade: {grade}
            Language: {language}
            
            Please provide:
            1. Explanation suitable for grade {grade}
            2. 3-4 learning activities
            3. Key vocabulary words (5-8 words)
            
            Format the response clearly with sections for explanation, activities, and vocabulary.
            Use your best judgment for any missing information.
            """
            
            response = model.generate_content(prompt)
            content = response.text
            
            # Parse the response (in real implementation, you might want more structured parsing)
            content_by_grade[f"grade_{grade}"] = {
                "explanation": content,
                "grade_level": grade,
                "complexity": complexity,
                "activities_suggested": activities,
                "vocabulary_level": vocabulary_level
            }
        
        return {
            "status": "success",
            "topic": topic,
            "subject": subject,
            "language": language,
            "grade_levels": grade_levels,
            "content_by_grade": content_by_grade,
            "timestamp": current_time,
            "defaults_used": {
                "language_defaulted": language == "English" and not locals().get('original_language'),
                "subject_defaulted": subject == "General Studies" and not locals().get('original_subject')
            },
            "message": f"Multi-grade content created for {len(grade_levels)} grade levels"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Error creating multi-grade content: {str(e)}",
        }


def translate_and_localize(content: str, target_language: str, cultural_adaptations: Optional[List[str]] = None) -> str:
    """
    Translate content and adapt it for local cultural context using Gemini AI.
    
    Translates educational content to a target language while adapting cultural references,
    examples, and context to make it more relevant for local students and teachers.
    
    Args:
        content (str): The original content to translate and localize (required)
        target_language (str): The target language for translation (required)
        cultural_adaptations (Optional[List[str]]): Specific cultural adaptations to apply (defaults to general Indian context if None)
    
    Returns:
        str: Translated and culturally adapted content in the target language
        
    Examples:
        translate_and_localize("Spring season story", "Hindi", ["festivals", "food"])
        translate_and_localize("Math explanation", "Telugu", None)
    """
    print(f"--- Tool: translate_and_localize called for {target_language} ---")
    
    try:
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create cultural adaptation instructions
        adaptations_text = ", ".join(cultural_adaptations) if cultural_adaptations else "general local cultural context"
        
        # Craft prompt for translation and localization
        prompt = f"""
        Translate and culturally adapt the following content to {target_language} language.
        
        Original Content: {content}
        Target Language: {target_language}
        Cultural Adaptations Needed: {adaptations_text}
        
        Requirements:
        - Translate accurately to {target_language}
        - Adapt cultural references to local context
        - Replace foreign examples with local Indian examples
        - Use culturally appropriate metaphors and analogies
        - Maintain educational value while making it locally relevant
        - Include local festivals, foods, places, or customs where appropriate
        
        Please provide the translated and localized content only.
        """
        
        response = model.generate_content(prompt)
        translated_content = response.text
        
        return translated_content
        
    except Exception as e:
        return f"Error in translation: {str(e)}"


def handle_minimal_request(user_request: str) -> str:
    """
    Handle requests with minimal information by intelligently inferring context and providing appropriate content.
    
    Analyzes vague or incomplete educational requests and generates appropriate content using
    smart defaults and context inference. Suitable for teachers who need quick educational content.
    
    Args:
        user_request (str): The minimal or vague educational request from the user
    
    Returns:
        str: Generated educational content that fulfills the request with appropriate defaults
        
    Examples:
        handle_minimal_request("Tell me about animals")
        handle_minimal_request("Something for grade 3 math")
    """
    print(f"--- Tool: handle_minimal_request called for: {user_request} ---")
    
    try:
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create educational content based on the request
        content_prompt = f"""
        Based on this educational request: "{user_request}"
        
        Create appropriate educational content with these requirements:
        - Use English language with local terms where needed (suitable for Indian context)
        - Make it engaging and age-appropriate for school students
        - Include local cultural references where relevant
        - Provide practical, usable content for teachers
        - If the request is vague, use your best judgment to create valuable educational content
        - Make it interactive and engaging
        
        Original Request: {user_request}
        
        Please provide comprehensive educational content that fulfills the request.
        """
        
        content_response = model.generate_content(content_prompt)
        generated_content = content_response.text
        
        return generated_content
        
    except Exception as e:
        return f"Error handling request: {str(e)}"


def create_educational_image(request: str) -> dict:
    """
    Create educational images based on teacher requests using Google GenAI native image generation.
    Uploads the generated image to Google Cloud Storage and returns the public URL.
    
    Takes basic teacher requests and creates simple educational visuals.
    Returns a dictionary with the public image URL for easy use by both sub-agent and root agent.
    
    Args:
        request (str): Basic teacher request for visual content (required)
    
    Returns:
        dict: Dictionary containing image_url or error message
        
    Examples:
        create_educational_image("water cycle diagram")
        create_educational_image("photosynthesis flowchart")
    """
    print(f"--- Tool: create_educational_image called for: {request} ---")
    
    try:
        # Create Google GenAI client
        client = google_genai.Client()
        
        # Create educational image prompt
        contents = f"""Create a simple educational {request}. 
        Make it clear and easy to understand for students.
        Use bright colors, clear labels, and simple design suitable for classroom teaching."""
        
        # Generate image using the new Google GenAI API
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        # Process the response and upload to GCP bucket
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Convert image data to PIL Image
                image = Image.open(BytesIO(part.inline_data.data))
                
                # Convert back to bytes for upload
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                safe_request = "".join(c for c in request[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_request = safe_request.replace(' ', '_')
                filename = f"educational_images/{safe_request}_{timestamp}_{unique_id}.png"
                
                # Upload to GCP bucket
                public_url = upload_to_gcp_bucket(img_byte_arr.getvalue(), filename)
                
                if public_url:
                    print(f"✅ Image uploaded successfully: {public_url}")
                    return {
                        "image_url": public_url
                    }
                else:
                    return {
                        "error": "Failed to upload image to GCP bucket"
                    }
        
        # If no image data found, return error
        return {
            "error": "Image generation failed - no image data received"
        }
            
    except Exception as e:
        print(f"❌ Error in create_educational_image: {str(e)}")
        return {
            "error": f"Error creating educational image: {str(e)}"
        }


def upload_to_gcp_bucket(image_data: bytes, filename: str) -> str:
    """
    Upload image data to Google Cloud Storage bucket and return public URL.
    
    Args:
        image_data (bytes): The image data to upload
        filename (str): The filename/path for the uploaded file
        
    Returns:
        str: Public URL of the uploaded image, or None if upload failed
    """
    try:
        # Get bucket name from environment variable
        bucket_name = os.getenv("GCP_BUCKET_NAME", "hackathon_by_us")
        project_id = os.getenv("GCP_PROJECT_ID", "utility-range-466813-g7")
        
        # Initialize the Cloud Storage client
        storage_client = storage.Client(project=project_id)
        
        # Get the bucket
        bucket = storage_client.bucket(bucket_name)
        
        # Create a blob object
        blob = bucket.blob(filename)
        
        # Set the content type
        blob.content_type = 'image/png'
        
        # Upload the image data
        blob.upload_from_string(image_data, content_type='image/png')
        
        # Make the blob publicly accessible
        # blob.make_public()
        
        # Return the public URL
        public_url = f"https://storage.googleapis.com/{bucket_name}/{filename}"
        
        print(f"✅ Successfully uploaded to GCP: {public_url}")
        return public_url
        
    except Exception as e:
        print(f"❌ Error uploading to GCP bucket: {str(e)}")
        return None
