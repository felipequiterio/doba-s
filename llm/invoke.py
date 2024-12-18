import ollama
from openai import OpenAI
from llm import get_arguments
from utils.log import get_custom_logger
from config import OLLAMA_MODEL, OPENAI_MODEL

logger = get_custom_logger("INVOKE")

client = OpenAI()


def ollama_invoke(system_message: str, user_message: str, payload: dict) -> dict:
    tools = None
    if payload:
        tools = [{"type": "function", "function": payload}]

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    response = ollama.chat(model=OLLAMA_MODEL, messages=messages, tools=tools)

    if payload:
        response = get_arguments(response)
        return response

    return response["message"]["content"]


def openai_invoke(system_message: dict, user_message: dict, payload: dict) -> dict:
    tools = None
    if payload:
        tools = [{"type": "function", "function": payload}]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[system_message, user_message],
        tools=tools,
    )

    if payload:
        response = get_arguments(response)
        return response

    return response["message"]["content"]
