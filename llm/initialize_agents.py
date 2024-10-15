from llm.agent import AgentManager
from agents.todo_agent import create_todo_agent
from typing import List, Dict
from utils.log import get_custom_logger

logger = get_custom_logger("INITIALIZE AGENTS")


def initialize_agents() -> tuple[AgentManager, List[Dict[str, str]]]:
    logger.info("Initializing agents")
    agent_manager = AgentManager()

    # Adicionar o agente de todo list
    todo_agent = create_todo_agent()
    agent_manager.add_agent(todo_agent)

    # Adicione outros agentes aqui conforme necessário
    # Exemplo: agent_manager.add_agent(create_another_agent())

    # Criar uma lista formatada de agentes para uso em outras partes do código
    agent_list = [
        {
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "input_payload": agent.input_payload,
            "output_payload": agent.output_payload,
        }
        for agent in agent_manager.get_list()
    ]

    logger.info("Agents initialized")
    return agent_manager, agent_list
