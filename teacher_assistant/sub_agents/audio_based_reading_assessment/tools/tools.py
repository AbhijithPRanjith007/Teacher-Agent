import os
from datetime import datetime
from typing import List, Optional, Dict
import google.generativeai as genai
import json

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def provide_reading_passage(grade_level: str, passage_type: Optional[str] = None, topic: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Provide age-appropriate reading passages for students to read aloud during assessment.
    
    Creates or selects reading passages tailored to specific grade levels, topics, and languages
    for reading fluency and comprehension assessment purposes.
    
    Args:
        grade_level (str): Student's grade level (required)
        passage_type (Optional[str]): Type of passage - "story", "informational", "poetry" (defaults to "story")
        topic (Optional[str]): Specific topic or theme for the passage (optional)
        language (Optional[str]): Language for the passage - "English", "Hindi", "Tamil", etc. (defaults to "English")
    
    Returns:
        str: Grade-appropriate reading passage with instructions for the student
        
    Examples:
        provide_reading_passage("3", "story", "animals", "English")
        provide_reading_passage("5", "informational", "science", "Hindi")
    """
    print(f"--- Tool: provide_reading_passage called for grade {grade_level} in {language or 'English'} ---")
    
    try:
        # Set defaults if parameters not provided
        if not passage_type:
            passage_type = "story"
        if not language:
            language = "English"
        
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define grade-level reading characteristics
        grade_characteristics = {
            "1": {"words": "50-80", "sentences": "short, simple", "vocabulary": "basic sight words"},
            "2": {"words": "80-120", "sentences": "simple compound", "vocabulary": "familiar words"},
            "3": {"words": "120-180", "sentences": "varied length", "vocabulary": "grade-appropriate"},
            "4": {"words": "180-250", "sentences": "complex", "vocabulary": "expanded vocabulary"},
            "5": {"words": "250-350", "sentences": "varied complexity", "vocabulary": "academic terms"},
            "6": {"words": "350-450", "sentences": "sophisticated", "vocabulary": "advanced terms"},
            "7": {"words": "450-550", "sentences": "complex structures", "vocabulary": "mature vocabulary"},
            "8": {"words": "550-650", "sentences": "advanced", "vocabulary": "sophisticated terms"}
        }
        
        characteristics = grade_characteristics.get(grade_level, grade_characteristics["5"])
        
        # Create passage generation prompt with language support
        prompt = f"""
        Create a reading passage for a grade {grade_level} student to read aloud during a reading assessment.
        
        LANGUAGE REQUIREMENT: Create the passage in {language}
        
        PASSAGE REQUIREMENTS:
        - Type: {passage_type}
        - Topic: {topic if topic else "age-appropriate general topic"}
        - Length: {characteristics['words']} words
        - Sentence Structure: {characteristics['sentences']}
        - Vocabulary Level: {characteristics['vocabulary']}
        - Grade Level: {grade_level}
        - Language: {language}
        
        CONTENT GUIDELINES:
        - Make it engaging and interesting for grade {grade_level} students
        - Include appropriate vocabulary for the grade level in {language}
        - Ensure content is educationally valuable
        - Use culturally appropriate context for {language} speakers
        - Make it suitable for oral reading assessment
        - If language is not English, use proper script and cultural context
        
        FORMATTING REQUIREMENTS:
        1. Provide clear title in {language}
        2. Include the complete passage in {language}
        3. Add simple instructions for the student in {language}
        4. Suggest reading pace if needed
        
        Please create a complete, ready-to-use reading passage in {language} that teachers can immediately use for assessment.
        Focus on creating content that will effectively assess reading fluency, accuracy, and expression in {language}.
        """
        
        response = model.generate_content(prompt)
        reading_passage = response.text
        
        return reading_passage
        
    except Exception as e:
        return f"Error generating reading passage: {str(e)}"


def assess_live_reading_fluency(transcribed_audio: str, grade_level: str, passage_text: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Assess student's reading fluency based on live audio transcription and grade level.
    
    Analyzes reading speed, accuracy, expression, and comprehension in real-time
    as the student reads aloud during a live assessment session.
    
    Args:
        transcribed_audio (str): Live transcribed text from student's real-time reading (required)
        grade_level (str): Student's grade level (1-12) for age-appropriate assessment (required)
        passage_text (Optional[str]): Original passage text for accuracy comparison (optional)
        language (Optional[str]): Language of the reading assessment (defaults to "English")
    
    Returns:
        str: Detailed real-time reading fluency assessment with scores, feedback, and recommendations
        
    Examples:
        assess_live_reading_fluency("The cat sat on the mat...", "3", "Original passage text", "English")
        assess_live_reading_fluency("Student live reading...", "5", None, "Hindi")
    """
    print(f"--- Tool: assess_live_reading_fluency called for grade {grade_level} in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define grade-level expectations
        grade_expectations = {
            "1": {"wpm": "60-90", "accuracy": "90-95%", "level": "beginning reader"},
            "2": {"wpm": "90-120", "accuracy": "92-97%", "level": "developing reader"},
            "3": {"wpm": "120-150", "accuracy": "95-98%", "level": "transitional reader"},
            "4": {"wpm": "150-180", "accuracy": "96-99%", "level": "fluent reader"},
            "5": {"wpm": "180-200", "accuracy": "97-99%", "level": "advanced reader"},
            "6": {"wpm": "200-220", "accuracy": "98-99%", "level": "proficient reader"},
            "7": {"wpm": "220-240", "accuracy": "98-99%", "level": "advanced proficient"},
            "8": {"wpm": "240-260", "accuracy": "99%", "level": "skilled reader"}
        }
        
        expected = grade_expectations.get(grade_level, grade_expectations["5"])
        
        # Create live assessment prompt with language support
        prompt = f"""
        Assess this student's LIVE reading performance for grade {grade_level} in {language}:
        
        STUDENT READING (LIVE TRANSCRIPTION):
        {transcribed_audio}
        
        ORIGINAL PASSAGE (if available):
        {passage_text if passage_text else "Not provided - assess based on live transcription"}
        
        LANGUAGE: {language}
        GRADE {grade_level} EXPECTATIONS:
        - Reading Speed: {expected['wpm']} words per minute
        - Accuracy Rate: {expected['accuracy']}
        - Reading Level: {expected['level']}
        
        LANGUAGE-SPECIFIC ASSESSMENT:
        - Consider pronunciation standards specific to {language}
        - Evaluate phonetic accuracy appropriate for {language}
        - Assess vocabulary usage in {language}
        - Consider cultural context for {language} content
        
        Please provide a comprehensive assessment in {language} including:
        
        1. FLUENCY ANALYSIS:
        - Estimated reading speed (words per minute)
        - Reading accuracy percentage (if original text provided)
        - Expression and intonation quality appropriate for {language}
        - Pause patterns and phrasing in {language}
        
        2. PRONUNCIATION ASSESSMENT:
        - Correct pronunciation of words in {language}
        - Language-specific phonetic accuracy
        - Common mispronunciations identified for {language}
        
        3. COMPREHENSION INDICATORS:
        - Evidence of understanding from reading style
        - Appropriate pacing for comprehension in {language}
        - Expression matching content meaning
        
        4. GRADE-LEVEL COMPARISON:
        - Performance vs. grade {grade_level} expectations for {language}
        - Areas of strength in {language} reading
        - Areas needing improvement specific to {language}
        
        5. SPECIFIC FEEDBACK:
        - Positive aspects of {language} reading
        - Specific skills to work on for {language}
        - Recommended practice activities in {language}
        
        6. OVERALL SCORE:
        - Reading level assessment in {language} (Below/At/Above grade level)
        - Specific grade level equivalent if different
        - Progress recommendations for {language} reading
        
        Format the assessment clearly for teachers and parents to understand.
        Include specific, actionable recommendations for improvement in {language}.
        Provide the complete assessment in {language}.
        """
        
        response = model.generate_content(prompt)
        assessment_result = response.text
        
        return assessment_result
        
    except Exception as e:
        return f"Error assessing live reading fluency: {str(e)}"


def assess_reading_fluency(audio_text: str, grade_level: str, passage_text: Optional[str] = None, language: Optional[str] = None) -> str:
    """
    Assess student's reading fluency based on transcribed audio and grade level.
    
    Analyzes reading speed, accuracy, expression, and comprehension appropriate 
    for the student's grade level using educational assessment standards.
    
    Args:
        audio_text (str): Transcribed text from student's audio reading (required)
        grade_level (str): Student's grade level (1-12) for age-appropriate assessment (required)
        passage_text (Optional[str]): Original passage text for accuracy comparison (optional)
        language (Optional[str]): Language of the reading assessment (defaults to "English")
    
    Returns:
        str: Detailed reading fluency assessment with scores, feedback, and recommendations
        
    Examples:
        assess_reading_fluency("The cat sat on the mat...", "3", None, "English")
        assess_reading_fluency("Student reading text...", "5", "Original passage text...", "Hindi")
    """
    print(f"--- Tool: assess_reading_fluency called for grade {grade_level} in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Define grade-level expectations
        grade_expectations = {
            "1": {"wpm": "60-90", "accuracy": "90-95%", "level": "beginning reader"},
            "2": {"wpm": "90-120", "accuracy": "92-97%", "level": "developing reader"},
            "3": {"wpm": "120-150", "accuracy": "95-98%", "level": "transitional reader"},
            "4": {"wpm": "150-180", "accuracy": "96-99%", "level": "fluent reader"},
            "5": {"wpm": "180-200", "accuracy": "97-99%", "level": "advanced reader"},
            "6": {"wpm": "200-220", "accuracy": "98-99%", "level": "proficient reader"},
            "7": {"wpm": "220-240", "accuracy": "98-99%", "level": "advanced proficient"},
            "8": {"wpm": "240-260", "accuracy": "99%", "level": "skilled reader"}
        }
        
        expected = grade_expectations.get(grade_level, grade_expectations["5"])
        
        # Create assessment prompt with language support
        prompt = f"""
        Assess this student's reading performance for grade {grade_level} in {language}:
        
        STUDENT READING (TRANSCRIBED):
        {audio_text}
        
        ORIGINAL PASSAGE (if available):
        {passage_text if passage_text else "Not provided - assess based on transcribed content only"}
        
        LANGUAGE: {language}
        GRADE {grade_level} EXPECTATIONS:
        - Reading Speed: {expected['wpm']} words per minute
        - Accuracy Rate: {expected['accuracy']}
        - Reading Level: {expected['level']}
        
        LANGUAGE-SPECIFIC ASSESSMENT for {language}:
        - Consider pronunciation standards specific to {language}
        - Evaluate phonetic accuracy appropriate for {language}
        - Assess vocabulary usage in {language}
        - Consider cultural context for {language} content
        
        Please provide a comprehensive assessment in {language} including:
        
        1. FLUENCY ANALYSIS:
        - Estimated reading speed (words per minute)
        - Reading accuracy percentage (if original text provided)
        - Expression and intonation quality
        - Pause patterns and phrasing
        
        2. PRONUNCIATION ASSESSMENT:
        - Correct pronunciation of words in {language}
        - Common mispronunciations identified
        - Phonetic accuracy for grade level in {language}
        
        3. COMPREHENSION INDICATORS:
        - Evidence of understanding from reading style
        - Appropriate pacing for comprehension
        - Expression matching content meaning
        
        4. GRADE-LEVEL COMPARISON:
        - Performance vs. grade {grade_level} expectations for {language}
        - Areas of strength in {language} reading
        - Areas needing improvement specific to {language}
        
        5. SPECIFIC FEEDBACK:
        - Positive aspects of reading in {language}
        - Specific skills to work on
        - Recommended practice activities
        
        6. OVERALL SCORE:
        - Reading level assessment (Below/At/Above grade level)
        - Specific grade level equivalent if different
        - Progress recommendations
        
        Format the assessment clearly for teachers and parents to understand.
        Include specific, actionable recommendations for improvement.
        Provide the complete assessment in {language}.
        """
        
        response = model.generate_content(prompt)
        assessment_result = response.text
        
        return assessment_result
        
    except Exception as e:
        return f"Error assessing reading fluency: {str(e)}"


def analyze_pronunciation_accuracy(audio_text: str, target_words: List[str], grade_level: str, language: Optional[str] = None) -> str:
    """
    Analyze pronunciation accuracy of specific target words based on grade level phonics expectations.
    
    Evaluates student's pronunciation of target vocabulary words, identifying 
    phonetic patterns and providing grade-appropriate pronunciation feedback.
    
    Args:
        audio_text (str): Transcribed text from student's audio (required)
        target_words (List[str]): List of specific words to assess pronunciation for (required)
        grade_level (str): Student's grade level for phonics expectations (required)
        language (Optional[str]): Language of the assessment (defaults to "English")
    
    Returns:
        str: Detailed pronunciation analysis with word-by-word feedback and phonics guidance
        
    Examples:
        analyze_pronunciation_accuracy("cat bat mat", ["cat", "bat", "mat"], "1", "English")
        analyze_pronunciation_accuracy("photograph elephant", ["photograph", "elephant"], "4", "Hindi")
    """
    print(f"--- Tool: analyze_pronunciation_accuracy called for {len(target_words)} words in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create pronunciation analysis prompt with language support
        prompt = f"""
        Analyze pronunciation accuracy for a grade {grade_level} student in {language}:
        
        STUDENT AUDIO (TRANSCRIBED):
        {audio_text}
        
        TARGET WORDS TO ASSESS:
        {', '.join(target_words)}
        
        LANGUAGE: {language}
        GRADE {grade_level} PHONICS EXPECTATIONS for {language}:
        - Focus on age-appropriate phonetic patterns
        - Consider developmental pronunciation milestones
        - Evaluate against grade-level phonics standards for {language}
        
        Please provide analysis in {language}:
        
        1. WORD-BY-WORD ANALYSIS:
        For each target word, assess:
        - Whether the word appears in the transcription
        - Pronunciation accuracy (correct/incorrect/partially correct)
        - Specific phonetic errors if any
        - Phonics patterns demonstrated in {language}
        
        2. PHONETIC PATTERNS for {language}:
        - Consonant sound accuracy
        - Vowel sound accuracy
        - Blending abilities
        - Common phonetic substitutions in {language}
        
        3. GRADE-LEVEL ASSESSMENT:
        - Performance compared to grade {grade_level} expectations for {language}
        - Phonics skills demonstrated
        - Areas of phonetic strength
        - Areas needing phonics support in {language}
        
        4. SPECIFIC RECOMMENDATIONS:
        - Phonics activities for improvement in {language}
        - Practice words with similar patterns
        - Teaching strategies for identified errors
        
        5. PRONUNCIATION SCORE:
        - Overall pronunciation accuracy percentage
        - Individual word scores
        - Progress toward grade-level proficiency in {language}
        
        Format clearly for teachers to use in reading instruction planning.
        Include specific phonics teaching suggestions for {language}.
        Provide the complete analysis in {language}.
        """
        
        response = model.generate_content(prompt)
        pronunciation_analysis = response.text
        
        return pronunciation_analysis
        
    except Exception as e:
        return f"Error analyzing pronunciation: {str(e)}"


def evaluate_reading_comprehension(audio_text: str, comprehension_questions: List[str], grade_level: str, language: Optional[str] = None) -> str:
    """
    Evaluate reading comprehension based on student's verbal responses to questions.
    
    Assesses understanding, inference skills, and critical thinking appropriate 
    for the student's grade level through analysis of spoken responses.
    
    Args:
        audio_text (str): Transcribed responses from student (required)
        comprehension_questions (List[str]): Questions that were asked (required)
        grade_level (str): Student's grade level for appropriate expectations (required)
        language (Optional[str]): Language of the assessment (defaults to "English")
    
    Returns:
        str: Comprehensive reading comprehension evaluation with skill analysis and recommendations
        
    Examples:
        evaluate_reading_comprehension("The story was about...", ["What was the main idea?"], "3", "English")
        evaluate_reading_comprehension("I think the character felt...", ["How did the character feel?"], "5", "Hindi")
    """
    print(f"--- Tool: evaluate_reading_comprehension called for {len(comprehension_questions)} questions in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create comprehension evaluation prompt with language support
        prompt = f"""
        Evaluate reading comprehension for a grade {grade_level} student in {language}:
        
        COMPREHENSION QUESTIONS ASKED:
        {chr(10).join([f"{i+1}. {q}" for i, q in enumerate(comprehension_questions)])}
        
        STUDENT RESPONSES (TRANSCRIBED):
        {audio_text}
        
        LANGUAGE: {language}
        GRADE {grade_level} COMPREHENSION EXPECTATIONS for {language}:
        - Age-appropriate understanding levels
        - Expected vocabulary usage in {language}
        - Reasoning and inference skills for this grade
        
        Please provide evaluation in {language}:
        
        1. RESPONSE ANALYSIS:
        For each question and response:
        - Quality of understanding demonstrated
        - Accuracy of content recall
        - Evidence of deeper comprehension
        - Use of grade-appropriate vocabulary in {language}
        
        2. COMPREHENSION SKILLS ASSESSMENT:
        - Literal comprehension (basic facts)
        - Inferential comprehension (reading between lines)
        - Critical thinking and analysis
        - Personal connections to text
        
        3. GRADE-LEVEL PERFORMANCE:
        - Performance vs. grade {grade_level} standards for {language}
        - Vocabulary usage appropriateness
        - Complexity of thinking demonstrated
        - Areas of comprehension strength
        
        4. AREAS FOR IMPROVEMENT:
        - Specific comprehension skills to develop
        - Question types that need more practice
        - Strategies to improve understanding in {language}
        
        5. TEACHING RECOMMENDATIONS:
        - Comprehension strategies to teach
        - Types of questions to practice
        - Reading activities to support growth in {language}
        
        6. COMPREHENSION SCORE:
        - Overall comprehension level
        - Individual skill area scores
        - Grade-level equivalency
        
        Format for easy use by teachers in planning reading instruction.
        Include specific activities and strategies for {language}.
        Provide the complete evaluation in {language}.
        """
        
        response = model.generate_content(prompt)
        comprehension_evaluation = response.text
        
        return comprehension_evaluation
        
    except Exception as e:
        return f"Error evaluating comprehension: {str(e)}"


def generate_reading_level_report(audio_text: str, grade_level: str, assessment_type: str, language: Optional[str] = None) -> str:
    """
    Generate comprehensive reading level assessment report based on audio analysis.
    
    Creates detailed reports comparing student performance to grade-level expectations
    and provides actionable recommendations for reading improvement.
    
    Args:
        audio_text (str): Complete transcribed audio from reading assessment (required)
        grade_level (str): Student's current grade level (required)
        assessment_type (str): Type of assessment - "fluency", "comprehension", "complete" (required)
        language (Optional[str]): Language of the assessment (defaults to "English")
    
    Returns:
        str: Comprehensive reading assessment report with scores, analysis, and recommendations
        
    Examples:
        generate_reading_level_report("Student reading sample...", "4", "complete", "English")
        generate_reading_level_report("Fluency test reading...", "2", "fluency", "Hindi")
    """
    print(f"--- Tool: generate_reading_level_report called for {assessment_type} assessment in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create comprehensive report prompt with language support
        prompt = f"""
        Generate a comprehensive reading assessment report for a grade {grade_level} student in {language}:
        
        STUDENT READING SAMPLE (TRANSCRIBED):
        {audio_text}
        
        ASSESSMENT TYPE: {assessment_type}
        STUDENT GRADE LEVEL: {grade_level}
        LANGUAGE: {language}
        
        Please create a complete reading assessment report in {language} including:
        
        1. EXECUTIVE SUMMARY:
        - Overall reading level determination
        - Key strengths and areas for improvement
        - Grade-level comparison summary for {language}
        
        2. DETAILED ASSESSMENT RESULTS:
        Based on {assessment_type} focus:
        - Reading fluency analysis (speed, accuracy, expression)
        - Pronunciation and phonics evaluation for {language}
        - Comprehension indicators from reading style
        - Vocabulary usage assessment in {language}
        
        3. GRADE-LEVEL BENCHMARKING:
        - Performance vs. grade {grade_level} expectations for {language}
        - Reading level equivalent (below/at/above grade level)
        - Specific skill comparisons to benchmarks
        
        4. PROGRESS TRACKING:
        - Areas showing strength
        - Skills needing development
        - Priority areas for instruction in {language}
        
        5. INSTRUCTIONAL RECOMMENDATIONS:
        - Specific teaching strategies for {language}
        - Recommended reading materials
        - Practice activities for improvement
        - Frequency of assessment recommendations
        
        6. PARENT COMMUNICATION:
        - Summary for parents in simple language
        - Home support suggestions for {language}
        - Reading goals for family practice
        
        7. NEXT STEPS:
        - Short-term goals (next 4-6 weeks)
        - Long-term objectives (next semester)
        - Assessment schedule recommendations
        
        8. SCORES AND METRICS:
        - Numerical scores where applicable
        - Percentile rankings for grade level
        - Progress indicators
        
        Format the report professionally for educational use.
        Include specific, actionable recommendations for {language}.
        Make it useful for teachers, parents, and intervention planning.
        Provide the complete report in {language}.
        """
        
        response = model.generate_content(prompt)
        assessment_report = response.text
        
        return assessment_report
        
    except Exception as e:
        return f"Error generating reading report: {str(e)}"


def create_personalized_reading_plan(student_assessment: str, grade_level: str, focus_areas: List[str], language: Optional[str] = None) -> str:
    """
    Create personalized reading improvement plan based on assessment results.
    
    Develops individualized reading instruction plans with specific activities,
    timelines, and progress monitoring strategies based on identified needs.
    
    Args:
        student_assessment (str): Results from previous reading assessments (required)
        grade_level (str): Student's grade level (required)
        focus_areas (List[str]): Specific areas to focus on (e.g., ["fluency", "comprehension"]) (required)
        language (Optional[str]): Language of the plan (defaults to "English")
    
    Returns:
        str: Personalized reading improvement plan with activities, timeline, and progress monitoring
        
    Examples:
        create_personalized_reading_plan("Assessment results...", "3", ["fluency", "phonics"], "English")
        create_personalized_reading_plan("Reading evaluation...", "5", ["comprehension", "vocabulary"], "Hindi")
    """
    print(f"--- Tool: create_personalized_reading_plan called for focus areas: {focus_areas} in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create personalized plan prompt with language support
        prompt = f"""
        Create a personalized reading improvement plan for a grade {grade_level} student in {language}:
        
        STUDENT ASSESSMENT RESULTS:
        {student_assessment}
        
        FOCUS AREAS FOR IMPROVEMENT:
        {', '.join(focus_areas)}
        
        STUDENT GRADE LEVEL: {grade_level}
        LANGUAGE: {language}
        
        Please create a comprehensive plan in {language} including:
        
        1. INDIVIDUALIZED GOALS:
        - Specific, measurable objectives for each focus area
        - Timeline for achieving each goal
        - Success criteria and benchmarks for {language}
        
        2. DAILY ACTIVITIES:
        - 15-20 minutes of daily reading activities in {language}
        - Specific exercises for each focus area
        - Variety of engaging activities to maintain interest
        
        3. WEEKLY PRACTICE SCHEDULE:
        - Monday through Friday activity plan
        - Weekend enrichment activities
        - Balance of different skill practices in {language}
        
        4. INSTRUCTIONAL STRATEGIES:
        - Teaching methods for each focus area
        - Scaffolding approaches for skill building
        - Multi-sensory learning activities for {language}
        
        5. RESOURCES AND MATERIALS:
        - Recommended books at appropriate reading level in {language}
        - Digital tools and apps for practice
        - Games and activities for skill reinforcement
        
        6. PROGRESS MONITORING:
        - Weekly assessment checkpoints
        - Data collection methods
        - Adjustment criteria for plan modification
        
        7. FAMILY INVOLVEMENT:
        - Home practice activities
        - Parent guidance for supporting reading in {language}
        - Ways families can reinforce school learning
        
        8. DIFFERENTIATION STRATEGIES:
        - Accommodations for learning differences
        - Extension activities for rapid progress
        - Multiple pathways to goal achievement
        
        9. TIMELINE AND MILESTONES:
        - 4-week short-term goals
        - 8-week intermediate checkpoints
        - End-of-semester target achievements
        
        Make the plan practical, engaging, and achievable for {language}.
        Include specific activity examples and clear instructions.
        Ensure activities are appropriate for grade {grade_level} development level.
        Provide the complete plan in {language}.
        """
        
        response = model.generate_content(prompt)
        reading_plan = response.text
        
        return reading_plan
        
    except Exception as e:
        return f"Error creating reading plan: {str(e)}"


def track_reading_progress(previous_assessments: List[str], current_assessment: str, grade_level: str, language: Optional[str] = None) -> str:
    """
    Track and analyze reading progress over time by comparing multiple assessments.
    
    Analyzes trends in reading development, identifies areas of improvement or concern,
    and provides data-driven recommendations for continued instruction.
    
    Args:
        previous_assessments (List[str]): List of historical assessment results (required)
        current_assessment (str): Most recent assessment results (required)
        grade_level (str): Student's current grade level (required)
        language (Optional[str]): Language of the assessments (defaults to "English")
    
    Returns:
        str: Progress tracking analysis with trends, growth patterns, and recommendations
        
    Examples:
        track_reading_progress(["Assessment 1...", "Assessment 2..."], "Current assessment...", "4", "English")
        track_reading_progress(["Previous evaluation..."], "Latest assessment...", "3", "Hindi")
    """
    print(f"--- Tool: track_reading_progress called with {len(previous_assessments)} historical assessments in {language or 'English'} ---")
    
    try:
        # Set default language if not provided
        if not language:
            language = "English"
            
        # Create Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create progress tracking prompt with language support
        prompt = f"""
        Analyze reading progress for a grade {grade_level} student in {language}:
        
        HISTORICAL ASSESSMENTS:
        {chr(10).join([f"Assessment {i+1}: {assessment}" for i, assessment in enumerate(previous_assessments)])}
        
        CURRENT ASSESSMENT:
        {current_assessment}
        
        STUDENT GRADE LEVEL: {grade_level}
        LANGUAGE: {language}
        
        Please provide comprehensive progress analysis in {language} including:
        
        1. GROWTH TRENDS:
        - Areas showing consistent improvement
        - Skills that have plateaued or declined
        - Rate of progress compared to expectations for {language}
        - Overall trajectory analysis
        
        2. SKILL-SPECIFIC PROGRESS:
        - Fluency development over time
        - Pronunciation and phonics growth in {language}
        - Comprehension skill advancement
        - Vocabulary expansion evidence
        
        3. COMPARATIVE ANALYSIS:
        - Progress compared to grade-level benchmarks for {language}
        - Growth relative to previous performance
        - Areas of accelerated vs. slower development
        
        4. PATTERN IDENTIFICATION:
        - Consistent strengths across assessments
        - Recurring challenges or difficulties
        - Seasonal or contextual performance variations
        
        5. INSTRUCTIONAL EFFECTIVENESS:
        - Evidence of teaching strategy success
        - Areas where instruction needs adjustment
        - Recommended changes to current approach for {language}
        
        6. GOAL ACHIEVEMENT:
        - Progress toward previously set goals
        - Goals that have been met or exceeded
        - Goals requiring timeline adjustment
        
        7. FUTURE PROJECTIONS:
        - Expected progress for next assessment period
        - Realistic goals for continued growth in {language}
        - Areas requiring intensive focus
        
        8. RECOMMENDATIONS:
        - Continue current successful strategies
        - Modify approaches for challenging areas
        - New interventions or supports needed for {language}
        - Timeline for next progress review
        
        Format the analysis to show clear progress patterns.
        Include specific data points and measurable changes.
        Provide actionable recommendations for continued instruction in {language}.
        Provide the complete analysis in {language}.
        """
        
        response = model.generate_content(prompt)
        progress_analysis = response.text
        
        return progress_analysis
        
    except Exception as e:
        return f"Error tracking reading progress: {str(e)}"