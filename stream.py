import os
import ollama
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("MODEL")


def sync(message):
    formatted_message = {"role": "user", "content": message}

    stream = ollama.chat(
        model=MODEL,
        messages=[formatted_message],
        stream=True,
    )
    for chunk in stream:
        print(chunk["message"]["content"], end="", flush=True)
    print()
