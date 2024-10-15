def _get_arguments(response: dict) -> dict:
    args = response["message"]["tool_calls"][0]["function"]["arguments"]
    return args
