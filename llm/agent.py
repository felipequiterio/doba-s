"""
Agent Module

This module provides a framework for managing AI agents and their tasks. It includes:

- AgentTask: A model for defining tasks with expected outputs
- Agent: An abstract base class for implementing different types of agents
- AgentHandler: A manager class for registering and retrieving agents

The module enables a flexible system for creating and managing various AI agents,
each capable of executing specific tasks based on their implementation.
"""

from pydantic import BaseModel
from typing import List, Dict
from utils.log import get_custom_logger
from abc import ABC, abstractmethod

logger = get_custom_logger("AGENT")


class AgentTask(BaseModel):
    task: str
    expected_output: str


class Agent(BaseModel, ABC):
    name: str
    description: str
    system_prompt: str
    input_payload: Dict
    output_payload: Dict

    @abstractmethod
    def execute(self, agent_task: AgentTask) -> Dict:
        pass


class AgentHandler:
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
