import os
import json
from typing import List
from llm.agent import Agent
from pydantic import BaseModel
from dotenv import load_dotenv
from llm.invoke import ollama_invoke
from llm import get_arguments as get_arguments
from utils.log import get_custom_logger

load_dotenv()
MODEL = os.getenv("MODEL")
logger = get_custom_logger("TASK")

tasks_payload = {
    "name": "route_agent",
    "description": "Route the query to one or multiple agents, handling single or multi-step tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "step_number": {
                            "type": "integer",
                            "description": "The step number of the query (starting from 1)",
                        },
                        "task": {
                            "type": "string",
                            "description": "Task description the agent needs to complete",
                        },
                        "agent": {
                            "type": "string",
                            "description": "The agent responsible for this task",
                        },
                        "expected_output": {
                            "type": "string",
                            "description": "What output is expected after completion of the task",
                        },
                        "is_async": {
                            "type": "boolean",
                            "description": "Whether this task should be performed asynchronously",
                        },
                    },
                    "required": ["step_number", "task", "agent"],
                },
            }
        },
        "required": ["steps"],
    },
}


class Task(BaseModel):
    step_number: int
    task: str
    agent: str
    expected_output: str
    is_async: bool


class TaskList(BaseModel):
    steps: List[Task]


def generate(message, agent_list: List[Agent]) -> TaskList:
    agents_available = "\n".join(
        [
            f"- **Name**: `{agent.name}`\n  **Description**: {agent.description}"
            for agent in agent_list
        ]
    )

    system = system = {
        "role": "system",
        "content": f"""
                You are an intelligent assistant responsible for routing queries to the appropriate agents.
                When a query is simple and can be handled by a single agent, route it directly to that agent with the necessary task information.
                
                For complex queries that require multiple steps or involve multiple agents:
                - Identify each step needed to complete the query. Each step should be a distinct task with a specific goal.
                - Assign a unique `step_number` to each task, starting from 1, indicating the order of execution.
                - Choose the most appropriate `agent` for each task, based on the task's requirements and the agent's capabilities.
                - For tasks that need to be executed asynchronously, set `is_async` to `true`. This will indicate that the task can be completed independently without blocking other tasks.
                - For each task, clearly describe the expected outcome in `expected_output`. This will guide the agent on the form and content of the response.
                
                If a task is complex and requires further subdivision, split it into smaller tasks that can be routed to the same agent or different agents. 
                Provide the complete list of subtasks and the order in which they should be executed.

                Ensure that the output structure follows this format:
                - `steps`: an array containing each task, where each task includes:
                    - `step_number`: the step in the sequence
                    - `task`: a detailed description of the task to be completed
                    - `agent`: the agent designated to handle the task
                    - `expected_output`: a description of what the agent should provide after completing the task
                    - `is_async`: whether this task is asynchronous
                    
                Example:
                [
                    {{
                        "step_number": 1,
                        "task": "Fetch the current weather for New York City",
                        "agent": "weather_agent",
                        "expected_output": "Current weather conditions in New York City",
                        "is_async": false
                    }},
                    {{
                        "step_number": 2,
                        "task": "Add 'Buy groceries' to the user's to-do list",
                        "agent": "todo_agent",
                        "expected_output": "Confirmation that 'Buy groceries' was added to the to-do list",
                        "is_async": true
                    }}
                ]

                Available agents:
                {agents_available}
                """,
    }

    user = {"role": "user", "content": message}
    logger.info(f"Sending task generation request with message: {message}")

    response = ollama_invoke(system, user, tasks_payload)

    tasks = json.loads(response["steps"])

    tasks_list = {"steps": tasks}

    tasks_list = TaskList.model_validate(tasks_list)
    logger.info(f"Successfully validated {len(tasks_list.steps)} tasks")
    logger.info(f"Task list: {json.dumps(tasks_list.model_dump(), indent=2)}")

    return tasks_list


def route(task_list: TaskList, agent_list: List[Agent]):
    logger.info("Starting task routing process")

    for task in task_list.steps:
        agent_name = task.agent
        task_description = task.task

        logger.info(f"Routing task #{task.step_number} to agent '{agent_name}'")

    logger.info("Task routing completed")
    return "Agent routed"

    # agents = {agent["name"]: agent for agent in agent_list}

    # for step in task_object:
    #     agent_name = step.agent
    #     task = step.task

    #     if agent_name in agents:
    #         agent = agents[agent_name]
    #         is_async = step.is_async

    #         # Logic to execute agent
    #         agent_response = agent.execute()
    #         print(f"Routing task '{task}' to agent '{agent_name}' (Async: {is_async})")
    #         print(agent_response)
    #     else:
    #         print(f"Agent '{agent_name}' not found in agent list.")
