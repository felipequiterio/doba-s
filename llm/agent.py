from pydantic import BaseModel
from typing import List, Dict, Any
from utils.log import get_custom_logger
from abc import ABC, abstractmethod

logger = get_custom_logger("AGENT")


class Agent(BaseModel, ABC):
    name: str
    description: str
    system_prompt: str
    input_payload: Dict
    output_payload: Dict
    data: Any

    @abstractmethod
    def execute(self, arguments: Dict) -> Dict:
        pass


class AgentManager:
    def __init__(self):
        self.agent_list: List[Agent] = []

    def add_agent(self, agent: Agent):
        logger.info(f"Adding agent: {agent.name}")
        self.agent_list.append(agent)

    def get_list(self) -> List[Agent]:
        return self.agent_list

    def get_agent(self, name: str) -> Agent:
        logger.info(f"Getting agent: {name}")
        for agent in self.agent_list:
            if agent.name == name:
                return agent
        return None
