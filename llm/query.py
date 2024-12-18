import os
from llm.invoke import ollama_invoke
from dotenv import load_dotenv
from utils.log import get_custom_logger

logger = get_custom_logger("QUERY")

load_dotenv()
MODEL = os.getenv("MODEL")

route_payload = {
    "name": "route_query",
    "description": "Route the query to a specific agent",
    "parameters": {
        "type": "object",
        "properties": {
            "agent": {
                "type": "string",
                "description": "Type of the agent: conversational, tool.",
            },
        },
        "required": ["agent"],
    },
}


def route(user_message: str) -> dict:
    logger.info("Routing message")

    system = """
            You are an intelligent assistant capable of routing queries. 
            If the user's query is conversational, route to conversational agent. 
            If it requires an action, route to the tool agent.
            """

    response = ollama_invoke(system, user_message, route_payload)
    return response
