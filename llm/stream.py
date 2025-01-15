import os
import ollama
from dotenv import load_dotenv

load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


def stream(message):
    formatted_message = {"role": "user", "content": message}

    stream = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[formatted_message],
        stream=True,
    )
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()
