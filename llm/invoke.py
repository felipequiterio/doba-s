import ollama
from openai import OpenAI
from config import OLLAMA_MODEL, OPENAI_MODEL
from llm import get_arguments
from utils.log import get_custom_logger


logger = get_custom_logger("INVOKE")

client = OpenAI()


def ollama_invoke(system_message: dict, user_message: dict, payload: dict) -> dict:
    tools = None
    if payload:
        tools = [{"type": "function", "function": payload}]

    response = ollama.chat(
        model=OLLAMA_MODEL, messages=[system_message, user_message], tools=tools
    )

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
