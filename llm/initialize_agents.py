from llm.agent import AgentHandler
from agents.todo_agent import create_todo_agent
from typing import List, Dict
from utils.log import get_custom_logger

logger = get_custom_logger("INITIALIZE AGENTS")


def initialize_agents() -> tuple[AgentHandler, List[Dict[str, str]]]:
    logger.info("Initializing agents")
    agent_manager = AgentHandler()

    todo_agent = create_todo_agent()
    agent_manager.add_agent(todo_agent)

    agent_list = agent_manager.get_list()

    logger.info("Agents initialized")
    return agent_manager, agent_list
