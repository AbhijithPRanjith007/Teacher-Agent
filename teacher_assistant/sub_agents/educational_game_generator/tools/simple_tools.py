"""
Simple working educational game generator
"""

def create_simple_quiz_game(topic: str, grade_level: str) -> str:
    """Create a simple quiz game"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Quiz: {topic}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .question {{ margin: 20px 0; }}
        button {{ padding: 10px; margin: 5px; }}
        .correct {{ background: green; color: white; }}
        .wrong {{ background: red; color: white; }}
    </style>
</head>
<body>
    <h1>{topic} Quiz - Grade {grade_level}</h1>
    <div id="game">
        <div class="question">
            <h3>Sample Question about {topic}</h3>
            <button onclick="answer(true)">Correct Answer</button>
            <button onclick="answer(false)">Wrong Answer</button>
        </div>
        <div id="score">Score: 0/1</div>
    </div>
    <script>
        let score = 0;
        function answer(correct) {{
            if (correct) {{
                score++;
                alert('Correct!');
            }} else {{
                alert('Try again!');
            }}
            document.getElementById('score').textContent = 'Score: ' + score + '/1';
        }}
    </script>
</body>
</html>"""


def create_simple_math_game(operation: str, grade_level: str) -> str:
    """Create a simple math game"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Math Game: {operation}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; text-align: center; }}
        input {{ padding: 10px; font-size: 18px; }}
        button {{ padding: 10px 20px; font-size: 16px; }}
    </style>
</head>
<body>
    <h1>{operation} Practice - Grade {grade_level}</h1>
    <div id="problem">2 + 3 = ?</div>
    <input type="number" id="answer" placeholder="Your answer">
    <button onclick="checkAnswer()">Submit</button>
    <div id="result"></div>
    <script>
        function checkAnswer() {{
            const userAnswer = document.getElementById('answer').value;
            const correctAnswer = 5;
            if (parseInt(userAnswer) === correctAnswer) {{
                document.getElementById('result').innerHTML = '<p style="color: green;">Correct!</p>';
            }} else {{
                document.getElementById('result').innerHTML = '<p style="color: red;">Try again!</p>';
            }}
        }}
    </script>
</body>
</html>"""