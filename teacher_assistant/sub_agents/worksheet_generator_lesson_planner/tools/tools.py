# Remove unused imports
from typing import List, Optional
import google.generativeai as genai
import os

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def analyze_uploaded_textbook_page(additional_context: Optional[str] = None) -> str:
    """
    Analyze textbook page images uploaded by users.
    
    This function works with the agent's vision capabilities to analyze 
    images present in the conversation.
    
    Args:
        additional_context (Optional[str]): Additional context about the textbook
    
    Returns:
        str: Signal for the agent to process the image using its vision capabilities
    """
    print("--- Tool: analyze_uploaded_textbook_page called ---")
    
    # Return a signal that indicates the agent should use its vision capabilities
    # to analyze any images present in the conversation
    analysis_instruction = f"""
Please analyze the uploaded textbook page image and provide a comprehensive analysis including:

1. CONTENT EXTRACTION:
- Extract all visible text content
- Identify main topics and subtopics  
- Note headings, subheadings, and key terms
- Describe diagrams, charts, and visual elements

2. EDUCATIONAL ANALYSIS:
- Identify the subject area
- Estimate the grade level or age group
- Extract key concepts and learning points
- Identify vocabulary terms or definitions

3. LEARNING OBJECTIVES:
- Infer what students should learn from this page
- Identify skills or knowledge being developed
- Note any activities or exercises present

4. STRUCTURAL ELEMENTS:
- Describe page layout and organization
- Note special features (boxes, highlights, etc.)
- Identify question types if present

5. CULTURAL CONTEXT:
- Note any cultural references or examples
- Identify local context if present

Additional Context: {additional_context or "None provided"}

Format as structured analysis for educational material generation.
"""
    
    return analysis_instruction


def generate_differentiated_worksheets(content_analysis: str, grade_levels: List[str], subject: Optional[str] = None) -> str:
    """
    Generate multiple worksheet versions tailored to different grade levels from analyzed textbook content.
    
    Creates differentiated worksheets with varying complexity, vocabulary, and activities
    based on the grade levels present in a multi-grade classroom setting.
    
    Args:
        content_analysis (str): Analysis of textbook content from image analysis (required)
        grade_levels (List[str]): List of grade levels to create worksheets for (required)
        subject (Optional[str]): Subject area override if needed
    
    Returns:
        str: Collection of differentiated worksheets organized by grade level with
             activities, questions, and instructions tailored to each grade
              
    Examples:
        generate_differentiated_worksheets(analysis_result, ["2", "3", "4"])
        generate_differentiated_worksheets(analysis_result, ["5", "6"], "Science")
    """
    print(f"--- Tool: generate_differentiated_worksheets called for grades: {grade_levels} ---")
    
    try:
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        all_worksheets = []
        
        for grade in grade_levels:
            # Determine appropriate complexity and activity types for each grade
            if int(grade) <= 3:
                complexity = "very simple with pictures, matching, and basic fill-in-the-blanks"
                activities = "coloring, drawing, simple matching, basic writing"
                question_types = "multiple choice, true/false, picture matching"
            elif int(grade) <= 6:
                complexity = "intermediate with short answers and explanations"
                activities = "short writing, diagrams, group work, simple experiments"
                question_types = "short answer, fill-in-the-blanks, diagram labeling"
            else:
                complexity = "advanced with detailed explanations and analysis"
                activities = "essays, research, critical thinking, presentations"
                question_types = "long answer, analysis, compare/contrast, problem solving"
            
            # Create worksheet prompt for each grade
            worksheet_prompt = f"""
            Create a complete, ready-to-print worksheet for grade {grade} students based on this textbook analysis.
            
            TEXTBOOK CONTENT ANALYSIS:
            {content_analysis}
            
            WORKSHEET SPECIFICATIONS:
            - Target Grade: {grade}
            - Difficulty Level: {complexity}
            - Activity Types: {activities}
            - Question Format: {question_types}
            - Subject Area: {subject if subject else "As identified from content"}
            
            REQUIRED WORKSHEET FORMAT:
            
            # [SUBJECT] WORKSHEET - GRADE {grade}
            **Topic:** [Main topic from textbook]
            **Name:** _________________________ **Date:** _____________
            **Time Limit:** 30-40 minutes
            
            ## Instructions:
            - Read all questions carefully before answering
            - Write your answers clearly in the spaces provided
            - Ask your teacher if you need help
            
            ## Section 1: [Question Type 1] (10 points)
            [Create 3-4 questions with proper answer spaces]
            
            ## Section 2: [Question Type 2] (10 points)  
            [Create 3-4 questions with proper answer spaces]
            
            ## Section 3: [Question Type 3] (10 points)
            [Create 2-3 questions with proper answer spaces]
            
            ## Bonus Section: (5 points)
            [Create 1 challenging question]
            
            **Total Points: 35**
            
            IMPORTANT REQUIREMENTS:
            1. Create exactly 8-10 questions total across all sections
            2. Include clear answer spaces with lines or boxes: _______
            3. Make questions directly related to the textbook content
            4. Use age-appropriate vocabulary for grade {grade}
            5. Include proper point values for each section
            6. Add visual elements description if needed (draw, color, etc.)
            7. Make it immediately printable without modifications
            8. Include Indian cultural context where relevant
            
            Generate the complete worksheet content now:
            """
            
            response = model.generate_content(worksheet_prompt)
            worksheet_content = response.text
            
            # Add grade header and worksheet content
            all_worksheets.append(f"# WORKSHEET FOR GRADE {grade}\n\n{worksheet_content}\n\n{'='*50}\n\n")
        
        return "".join(all_worksheets)
        
    except Exception as e:
        return f"Error generating worksheets: {str(e)}"


def create_lesson_plan(content_analysis: str, duration: Optional[str] = None, grade_levels: Optional[List[str]] = None) -> str:
    """
    Generate comprehensive lesson plans based on analyzed textbook content for multi-grade classrooms.
    
    Creates detailed lesson plans with learning objectives, activities, assessments,
    and differentiated instruction approaches suitable for multi-grade teaching.
    
    Args:
        content_analysis (str): Analysis of textbook content from image analysis (required)
        duration (Optional[str]): Lesson duration (defaults to 45 minutes if None)
        grade_levels (Optional[List[str]]): Target grade levels (defaults to mixed grades if None)
    
    Returns:
        str: Comprehensive lesson plan with objectives, activities, timeline, 
              resources, and differentiated instruction strategies formatted as markdown text
              
    Examples:
        create_lesson_plan(analysis_result, "60 minutes", ["3", "4", "5"])
        create_lesson_plan(analysis_result)
    """
    print(f"--- Tool: create_lesson_plan called ---")
    
    try:
        # Set defaults for optional parameters
        if not duration:
            duration = "45 minutes"
        if not grade_levels:
            grade_levels = ["mixed grades"]
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create comprehensive lesson plan prompt
        lesson_plan_prompt = f"""
        Create a detailed, practical lesson plan for multi-grade classroom teaching based on this textbook analysis.
        
        TEXTBOOK CONTENT ANALYSIS:
        {content_analysis}
        
        LESSON PLAN SPECIFICATIONS:
        - Duration: {duration}
        - Target Grades: {', '.join(grade_levels)}
        - Teaching Context: Indian multi-grade classroom
        - Format: Immediately usable by teachers
        
        REQUIRED LESSON PLAN STRUCTURE:
        
        # LESSON PLAN: [Clear, Engaging Title]
        
        ## Basic Information
        - **Subject**: [Subject from textbook analysis]
        - **Grade Levels**: {', '.join(grade_levels)}
        - **Duration**: {duration}
        - **Topic**: [Main topic from textbook page]
        - **Date**: ____________
        
        ## Learning Objectives
        By the end of this lesson, students will be able to:
        1. [Specific, measurable objective using action verbs - Knowledge level]
        2. [Specific, measurable objective using action verbs - Comprehension level]  
        3. [Specific, measurable objective using action verbs - Application level]
        4. [Additional objectives differentiated by grade level if needed]
        
        ## Prerequisites
        - [What students should already know]
        - [Required prior knowledge or skills]
        
        ## Materials and Resources
        ### Required Materials:
        - [List all physical materials needed]
        - [Textbook pages, worksheets, charts, etc.]
        
        ### Technology Needs:
        - [Any digital tools or equipment]
        
        ### Teacher Preparation:
        - [What teacher needs to prepare in advance]
        - [Setup requirements]
        
        ## Detailed Lesson Structure
        
        ### Opening/Hook (5-8 minutes)
        **Activity**: [Specific engaging activity to capture attention]
        **Instructions**: 
        - [Step-by-step teacher actions]
        - [Expected student responses]
        **Materials**: [What's needed for this section]
        
        ### Introduction to Topic (8-12 minutes)
        **Activity**: [How to introduce the main concept]
        **Key Points to Cover**:
        - [Main concept 1 with explanation]
        - [Main concept 2 with explanation] 
        - [Main concept 3 with explanation]
        **Teaching Strategy**: [Lecture, discussion, demonstration, etc.]
        **Differentiation**: 
        - Lower grades: [Simplified approach]
        - Higher grades: [More complex approach]
        
        ### Main Instruction/Exploration (15-20 minutes)
        **Activity 1**: [Detailed description of main learning activity]
        - Instructions: [Step-by-step process]
        - Student roles: [What students do]
        - Teacher role: [How teacher facilitates]
        
        **Activity 2**: [Second learning activity if needed]
        - [Similar detailed breakdown]
        
        **Key Vocabulary**: [Important terms to emphasize]
        **Common Misconceptions**: [What to watch for and correct]
        
        ### Guided Practice (8-12 minutes)
        **Activity**: [Hands-on practice with teacher guidance]
        **Instructions**:
        - [Specific steps for students to follow]
        - [How teacher provides support]
        **Assessment Strategy**: [How to check understanding during practice]
        
        ### Independent Work (5-8 minutes)
        **Activity**: [What students do independently]
        **Instructions**: [Clear directions for students]
        **Expected Outcomes**: [What students should produce]
        
        ### Closure/Summary (3-5 minutes)
        **Summary Activity**: [How to wrap up the lesson]
        **Key Takeaways**: [Main points to reinforce]
        **Preview**: [Connection to next lesson]
        
        ## Differentiated Instruction Strategies
        
        ### For Lower Grade Students:
        - [Specific accommodations and modifications]
        - [Simplified vocabulary and concepts]
        - [Additional support strategies]
        
        ### For Higher Grade Students:
        - [Extension activities and challenges]
        - [More complex applications]
        - [Leadership roles in group work]
        
        ### For All Learners:
        - [Universal strategies that benefit everyone]
        - [Multiple ways to demonstrate understanding]
        
        ## Assessment and Evaluation
        
        ### Formative Assessment (During Lesson):
        - [Specific methods to check understanding throughout]
        - [Questions to ask students]
        - [Observable behaviors indicating comprehension]
        
        ### Summative Assessment (End of Lesson):
        - [How to evaluate student learning]
        - [Specific criteria for success]
        
        ### Success Criteria:
        **Lower Grades**: [What success looks like for younger students]
        **Higher Grades**: [What success looks like for older students]
        
        ## Homework and Extension
        - [Specific homework assignments related to lesson]
        - [Optional extension activities for fast finishers]
        - [Family involvement suggestions]
        
        ## Teacher Reflection Notes
        - [Space for teacher to note what worked well]
        - [Space to note what needs improvement]
        - [Adjustments for next time]
        
        ## Additional Resources
        - [Supplementary materials]
        - [Related activities for future lessons]
        - [Websites, books, or videos for further learning]
        
        IMPORTANT: Make this lesson plan immediately usable by providing specific, actionable instructions that any teacher can follow step-by-step.
        """
        
        response = model.generate_content(lesson_plan_prompt)
        lesson_plan_content = response.text
        
        # Return the lesson plan content directly as markdown text
        return lesson_plan_content
        
    except Exception as e:
        return f"Error creating lesson plan: {str(e)}"


def create_learning_objectives(content_analysis: str, grade_levels: List[str], subject: Optional[str] = None) -> str:
    """Create comprehensive learning objectives from textbook content analysis."""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Create comprehensive, measurable learning objectives based on this textbook content analysis.
        
        TEXTBOOK CONTENT ANALYSIS:
        {content_analysis}
        
        TARGET GRADES: {', '.join(grade_levels)}
        SUBJECT AREA: {subject if subject else 'As identified from content'}
        
        REQUIRED FORMAT:
        # LEARNING OBJECTIVES - [SUBJECT] (GRADES {', '.join(grade_levels)})
        
        ## Knowledge Objectives (Students will KNOW):
        1. [Specific factual knowledge students should acquire]
        2. [Key concepts and terminology they should understand]
        3. [Important principles and theories to learn]
        
        ## Comprehension Objectives (Students will UNDERSTAND):
        1. [Deeper understanding of relationships and connections]
        2. [Ability to explain concepts in their own words]
        3. [Understanding of cause and effect relationships]
        
        ## Application Objectives (Students will be able to DO):
        1. [Practical skills students can demonstrate]
        2. [Problem-solving abilities they can apply]
        3. [Real-world applications they can perform]
        
        ## Analysis Objectives (Students will be able to ANALYZE):
        1. [Ability to break down complex information]
        2. [Compare and contrast different elements]
        3. [Identify patterns and relationships]
        
        ## Grade-Specific Differentiation:
        ### Lower Grades ({min(grade_levels)} - {str(int(min(grade_levels))+1)}):
        - [Simplified objectives appropriate for younger students]
        - [Basic knowledge and comprehension focus]
        
        ### Higher Grades ({str(int(max(grade_levels))-1)} - {max(grade_levels)}):
        - [More complex objectives for advanced students]
        - [Analysis and application focus]
        
        ## Assessment Criteria:
        Students will demonstrate mastery when they can:
        - [Observable behavior 1]
        - [Observable behavior 2]
        - [Observable behavior 3]
        
        IMPORTANT REQUIREMENTS:
        1. Use specific action verbs (define, explain, demonstrate, analyze, etc.)
        2. Make objectives measurable and observable
        3. Align with textbook content provided
        4. Differentiate for multiple grade levels
        5. Include both cognitive and practical objectives
        6. Ensure objectives are achievable within lesson timeframe
        
        Generate the complete learning objectives now:
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Error creating objectives: {str(e)}"