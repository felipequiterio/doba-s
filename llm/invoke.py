import ollama
from openai import OpenAI
from llm import get_arguments, ToolCallValidationError
from utils.log import get_custom_logger
from config import OLLAMA_MODEL, OPENAI_MODEL, DEEPSEEK_MODEL

logger = get_custom_logger("INVOKE")

client = OpenAI()


def model_invoke(
    system_message: str,
    user_message: str,
    payload: dict = None,
    model: str = "ollama",
) -> dict:
    if model == "ollama":
        return ollama_invoke(system_message, user_message, payload)
    elif model == "deepseek":
        return deepseek_invoke(system_message, user_message, payload)
    elif model == "openai":
        return openai_invoke(system_message, user_message, payload)
    else:
        raise ValueError(
            f"Invalid model: {model}. Models avaiable: ollama, deepseek, openai"
        )


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
        try:
            response = get_arguments(response)
            return response
        except ToolCallValidationError as e:
            logger.error(f"Tool call validation failed: {str(e)}")
            # Re-attempt the entire request
            logger.info("Retrying complete request...")
            return ollama_invoke(system_message, user_message, payload)

    return response["message"]["content"]


def deepseek_invoke(system_message: str, user_message: str, payload: dict) -> dict:
    tools = None
    if payload:
        tools = [{"type": "function", "function": payload}]

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    response = ollama.chat(model=DEEPSEEK_MODEL, messages=messages, tools=tools)

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
