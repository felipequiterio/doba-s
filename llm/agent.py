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
import llm
from llm import stream
from utils.log import get_custom_logger
from abc import ABC, abstractmethod

# from utils.printing import print_result

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


def run_agent(message: str, agent_manager: AgentHandler) -> None:
    logger.info(f"Processing message: {message}")

    # Determine if message should be handled conversationally or by a tool
    query_route = llm.query.route(message)
    agent_type = query_route["agent"]
    logger.info(f"Message routed to {agent_type} agent")

    match agent_type:
        case "conversational":
            # Handle conversational messages by streaming response
            stream(message)

        case "tool":
            # Handle tool requests by generating and routing specific tasks
            available_agents = agent_manager.get_list()
            tasks = llm.task.generate(message, available_agents)
            results = llm.task.route(tasks, available_agents)
            for result in results:
                print(result)
            final_answer = llm.task.generate_final_answer(message, results)
            # stream(final_answer)
            print(final_answer)

        case _:
            raise ValueError(f"Invalid agent type: {agent_type}")
