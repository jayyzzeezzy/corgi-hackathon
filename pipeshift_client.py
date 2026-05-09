import os

from dotenv import load_dotenv
import requests

load_dotenv()

PIPESHIFT_API_URL = "https://api.pipeshift.com/api/v0/chat/completions"
DEFAULT_MODEL = "moonshotai/Kimi-K2-Thinking"


def chat(messages: list[dict], model: str = DEFAULT_MODEL, temperature: float = 1.0) -> dict:
    api_key = os.environ.get("PIPESHIFT_API_KEY")
    if not api_key:
        raise ValueError("PIPESHIFT_API_KEY environment variable not set")

    response = requests.post(
        PIPESHIFT_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        },
    )
    response.raise_for_status()
    return response.json()


def ask(prompt: str, **kwargs) -> str:
    result = chat([{"role": "user", "content": prompt}], **kwargs)
    return result["choices"][0]["message"]["content"]
