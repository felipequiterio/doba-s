import json
import os
from typing import List, Dict, Any
import ollama
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from llm import _get_arguments as get_arguments
from llm.agent import AgentManager
from utils.log import get_custom_logger

load_dotenv()
MODEL = os.getenv("MODEL")

logger = get_custom_logger("TASK")


tasks_payload = {
    "type": "function",
    "function": {
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
    },
}


class Step(BaseModel):
    step_number: int
    task: str
    agent: str
    expected_output: str
    is_async: bool = False


class TaskList(BaseModel):
    steps: List[Step]


def generate(message):
    logger.info("Generating tasks")
    system = {
        "role": "system",
        "content": """
You are an intelligent assistant responsible for routing queries to the appropriate agents.
Your task is to analyze the user's request and generate a structured plan using the provided tool.
You must always use the 'route_agent' function to output your response.

Instructions:
1. Analyze the user's query.
2. Determine the necessary steps to complete the query.
3. For each step, provide ALL of the following information:
   - step_number: An integer starting from 1
   - task: A detailed description of what needs to be done
   - agent: The name of the agent responsible for this task (use 'todo_agent' for todo list related tasks)
   - expected_output: What should be produced after completing this task
   - is_async: Whether this task can be performed asynchronously (true or false)
4. Use the 'route_agent' function to structure your response.

Remember: You must always use the 'route_agent' function and include ALL required fields for each step.
Do not respond in any other format.
        """,
    }

    user = {"role": "user", "content": message}

    max_attempts = 3
    for attempt in range(max_attempts):
        response = ollama.chat(
            model=MODEL,
            messages=[system, user],
            tools=[tasks_payload],
        )

        logger.info(f"LLM response (attempt {attempt + 1}): {response}")

        if "tool_calls" in response["message"]:
            try:
                args = get_arguments(response)
                steps = args.get("steps")
                if isinstance(steps, str):
                    steps = json.loads(steps)

                # Attempt to fix and validate the structure
                fixed_steps = []
                for i, step in enumerate(steps, start=1):
                    fixed_step = {
                        "step_number": step.get("step_number", i),
                        "task": step.get("task", step.get("task_description", "")),
                        "agent": step.get("agent", step.get("agent_id", "todo_agent")),
                        "expected_output": step.get("expected_output", ""),
                        "is_async": step.get("is_async", False),
                    }
                    fixed_steps.append(Step(**fixed_step))

                tasks = TaskList(steps=fixed_steps)
                logger.info(f"Tasks generated: {tasks}")
                return tasks
            except ValidationError as e:
                logger.error(f"Validation error: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing response: {str(e)}")
        else:
            logger.warning(f"No tool call in response (attempt {attempt + 1})")

        # If we reach here, the response didn't contain a valid tool call or had validation errors
        # Add a message to explicitly request using the tool with all required fields
        user["content"] += (
            "\n\nPlease use the 'route_agent' function to structure your response, ensuring ALL required fields (step_number, task, agent, expected_output, is_async) are included for each step."
        )

    # If we've exhausted all attempts, raise an exception
    raise Exception("Failed to generate valid tasks after multiple attempts")


def route(task_object: TaskList, agent_manager: AgentManager):
    results = []
    for step in task_object.steps:
        agent_name = step.agent
        task = step.task

        agent = agent_manager.get_agent(agent_name)
        if agent:
            is_async = step.is_async
            expected_output = step.expected_output

            logger.info(
                f"Routing task '{task}' to agent '{agent_name}' (Async: {is_async})"
            )
            logger.info(f"Expected output: {expected_output}")

            result = execute(agent, task)
            results.append(result)
        else:
            logger.error(f"Agent '{agent_name}' not found in agent list.")
            results.append(
                {"success": False, "error": f"Agent '{agent_name}' not found"}
            )

    return results


def execute(agent, task):
    logger.info(f"Executing task for agent: {agent.name}")

    system_message = {"role": "system", "content": agent.system_prompt}
    user_message = {"role": "user", "content": task}

    try:
        response = ollama.chat(
            model=MODEL,
            messages=[system_message, user_message],
            tools=[agent.input_payload],
        )

        logger.info(f"LLM response: {response}")

        tool_call = response["message"].get("tool_calls", [{}])[0]
        if tool_call:
            function_args = tool_call["function"]["arguments"]
            if isinstance(function_args, str):
                function_args = json.loads(function_args)
            result = agent.execute(function_args)
            logger.info(f"Agent execution result: {result}")
            return result
        else:
            logger.error("No valid tool call in LLM response")
            return {"success": False, "error": "Failed to process LLM response"}
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}")
        return {"success": False, "error": f"Error executing task: {str(e)}"}
