# app/services/ai_feedback.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:0.5b"

def generate_feedback(code: str, rubric_criteria: dict, tone: str, test_results: list) -> str:
    """
    Generate AI feedback for a student's submission.
    
    Parameters:
        code: the student's submitted code
        rubric_criteria: dict containing criteria for grading
        tone: 'neutral', 'friendly', 'strict', etc.
        test_results: list of dicts with test case results
    Returns:
        AI feedback text
    """
    # Build a prompt for the AI
    prompt = f"""
        You are a senior programming instructor. Analyze the student's solution using the rubric below.
        Your job is to give concise but high-quality feedback that helps the student improve.

        ##########
        STUDENT CODE
        ##########
        {code}

        ##########
        RUBRIC CRITERIA
        ##########
        {json.dumps(rubric_criteria, indent=2)}

        ##########
        TEST RESULTS
        ##########
        {json.dumps(test_results, indent=2)}

        ##########
        INSTRUCTIONS
        ##########
        1. Start with a short overall evaluation.
        2. Then give bullet-point feedback grouped by rubric category:
        - Correctness
        - Input Validation
        - Algorithm Quality
        - Code Quality
        - Edge Cases
        3. Reference the failed test cases if any.
        4. Use the requested tone: {tone}.
        5. Do NOT rewrite full code. Give only guidance.

        Return ONLY the feedback text. Do not include explanations of what you are doing.
    """

    data = {
        "model": MODEL_NAME,
        "prompt": prompt
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, stream=True)
        full_text = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                full_text += chunk.get("response", "")
        return full_text.strip()
    except Exception as e:
        # fallback in case AI service fails
        return f"AI feedback could not be generated: {str(e)}"
