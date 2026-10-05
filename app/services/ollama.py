import requests


MODEL = "hf.co/HauhauCS/Qwen3.5-9B-Uncensored-HauhauCS-Aggressive:Q4_K_M"

OLLAMA_URL = "http://localhost:11434/api/generate"


def ask_qwen(prompt: str) -> str:

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.3
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600
    )

    response.raise_for_status()

    data = response.json()

    return data.get("response", "")