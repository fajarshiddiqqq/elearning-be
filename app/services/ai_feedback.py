import requests
import json
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:0.5b"

BASE_DIR = Path(__file__).resolve().parent
PROMPT_DIR = BASE_DIR / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def render(template: str, values: dict) -> str:
    for key, val in values.items():
        placeholder = "{{" + key + "}}"
        template = template.replace(placeholder, str(val))
    return template


def generate_feedback(status: str, code: str, rubric, score: float, custom_instructions: str):

    # Load templates
    system_template = load_prompt("system_prompt.txt")
    user_template = load_prompt("user_prompt.txt")

    # Render system prompt
    system_prompt = render(system_template, {
        "CUSTOM_INSTRUCTIONS": custom_instructions or "None"
    })

    # Render user prompt
    user_prompt = render(user_template, {
        "TEST_RESULTS": status,
        "CODE": code,
        "TEST_SCORE": score,
        "RUBRIC_JSON": json.dumps(rubric.criteria, indent=2)
    })

    payload = {
        "model": MODEL_NAME,
        "prompt": system_prompt + "\n" + user_prompt,
        "stream": True
    }

    # LLM call
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
    except Exception as e:
        return {"error": f"Ollama error: {str(e)}"}

    # Streaming parse
    raw = ""
    for line in response.iter_lines():
        if not line:
            continue
        try:
            chunk = json.loads(line.decode("utf-8"))
            raw += chunk.get("response", "")
        except:
            continue

    raw = raw.strip()

    # Try strict JSON parsing
    try:
        return json.loads(raw)
    except:
        pass

    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except:
        return {
            "error": "Model returned invalid JSON.",
            "raw_output": raw
        }
