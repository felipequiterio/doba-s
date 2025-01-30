import os
import json
from pydantic import BaseModel
from typing import Dict, Optional
from llm.invoke import model_invoke
from llm.agent import Agent, AgentTask
from utils.log import get_custom_logger

logger = get_custom_logger("Todo Agent")


todo_action_payload = {
    "name": "todo_action",
    "description": "Process a todo task action",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "object",
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["add"]},
                            "title": {
                                "type": "string",
                                "description": "Title of the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the task",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "Due date in YYYY-MM-DD format or 'none' if not applicable",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                        },
                        "required": ["type", "title", "due_date", "priority"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["update"]},
                            "id": {
                                "type": "integer",
                                "description": "ID of the task to update",
                            },
                            "title": {
                                "type": "string",
                                "description": "New title of the task",
                            },
                            "description": {
                                "type": "string",
                                "description": "New description of the task",
                            },
                            "due_date": {
                                "type": "string",
                                "description": "New due date in YYYY-MM-DD format or 'none' if not applicable",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"],
                            },
                        },
                        "required": ["type", "id"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["delete"]},
                            "id": {
                                "type": "integer",
                                "description": "ID of the task to delete",
                            },
                        },
                        "required": ["type", "id"],
                    },
                    {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["list"]},
                            "filter": {
                                "type": "string",
                                "enum": ["all", "status", "priority", "due_date"],
                            },
                            "filter_value": {
                                "type": "string",
                                "description": "Value to filter by (if applicable)",
                            },
                        },
                        "required": ["type", "filter"],
                    },
                ],
            }
        },
        "required": ["action"],
    },
}


class TodoAgent(Agent):
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        input_payload: Dict,
        output_payload: Dict,
    ):
        super().__init__(
            name=name,
            description=description,
            system_prompt=system_prompt,
            input_payload=input_payload,
            output_payload=output_payload,
        )

    def execute(self, agent_task: AgentTask) -> Dict:
        logger.info(f"Todo Agent executing task: {agent_task.task}")

        todo_task = model_invoke(
            system_message=self.system_prompt,
            user_message=agent_task.task,
            payload=todo_action_payload,
        )

        logger.info(f"Todo Agent RESPONSE:\n {json.dumps(todo_task, indent=2)}")

        action = todo_task["action"]

        match action["type"]:
            case "add":
                self.add_task(action)
            case "update":
                self.update_task(action)
            case "delete":
                self.delete_task(action)
            case "list":
                self.list_tasks(action)

        return todo_task

    def add_task(self, task: Dict) -> Dict:
        try:
            todo_list = []
            if (
                os.path.exists("todo_list.json")
                and os.path.getsize("todo_list.json") > 0
            ):
                with open("todo_list.json", "r") as f:
                    todo_list = json.load(f)
            else:
                # Create the file with an empty list if it doesn't exist
                with open("todo_list.json", "w") as f:
                    json.dump([], f)

            new_id = max([task.get("id", 0) for task in todo_list], default=0) + 1

            new_task = {
                "id": new_id,
                "title": task["title"],
                "description": task.get("description", ""),
                "due_date": task["due_date"],
                "priority": task["priority"],
                "status": "pending",
            }

            todo_list.append(new_task)

            with open("todo_list.json", "w") as f:
                json.dump(todo_list, f, indent=2)

            logger.info(f"Task added successfully with ID: {new_id}")
            return {
                "status": "success",
                "message": f"Task: #{new_id} - {task['title']} was added successfully",
            }

        except Exception as e:
            logger.error(f"Error adding task: {str(e)}")
            return {"status": "error", "message": f"Error adding task: {str(e)}"}

    def update_task(self, task: Dict) -> Dict:
        try:
            if (
                not os.path.exists("todo_list.json")
                or os.path.getsize("todo_list.json") == 0
            ):
                return {
                    "status": "error",
                    "message": "Todo list file is empty or doesn't exist",
                }

            with open("todo_list.json", "r") as f:
                todo_list = json.load(f)

            # Find the task with the matching ID
            task_index = next(
                (index for (index, t) in enumerate(todo_list) if t["id"] == task["id"]),
                -1,
            )

            if task_index == -1:
                return {
                    "status": "error",
                    "message": f"Task with ID {task['id']} not found",
                }

            # Update only the fields that are provided
            if "title" in task:
                todo_list[task_index]["title"] = task["title"]
            if "description" in task:
                todo_list[task_index]["description"] = task["description"]
            if "due_date" in task:
                todo_list[task_index]["due_date"] = task["due_date"]
            if "priority" in task:
                todo_list[task_index]["priority"] = task["priority"]
            if "status" in task:
                todo_list[task_index]["status"] = task["status"]

            # Save the updated list
            with open("todo_list.json", "w") as f:
                json.dump(todo_list, f, indent=2)

            logger.info(f"Task {task['id']} updated successfully")
            return {
                "status": "success",
                "message": f"Task #{task['id']} was updated successfully",
            }

        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return {"status": "error", "message": f"Error updating task: {str(e)}"}

    def delete_task(self, task: Dict) -> Dict:
        return logger.info("Task deleted!")

    def list_tasks(self, task: Dict) -> Dict:
        return logger.info("Tasks listed!")


def create_todo_agent() -> TodoAgent:
    """Returns an instance of the TodoAgent class."""
    return TodoAgent(
        name="TodoAgent",
        description="Agent responsible for managing a todo list, including adding, updating, deleting, and listing tasks with their priorities, due dates, and completion status",
        system_prompt="""You are a todo list manager that MUST ALWAYS return a complete action structure in your responses.

        Your response MUST ALWAYS follow this structure based on the action type:

        For ADD actions:
        {
            "action": {
                "type": "add",
                "title": "task title",
                "description": "detailed description",
                "due_date": "YYYY-MM-DD",
                "priority": "low|medium|high"
            }
        }

        For UPDATE actions:
        Note: If the field is not provided, it should be returned as an empty string.
        {
            "action": {
                "type": "update",
                "id": task_id,
                "title": "new title",
                "description": "new description",
                "due_date": "YYYY-MM-DD",
                "priority": "low|medium|high",
                "status": "pending|in_progress|completed"
            }
        }

        For DELETE actions:
        {
            "action": {
                "type": "delete",
                "id": task_id
            }
        }

        For LIST actions:
        {
            "action": {
                "type": "list",
                "filter": "all|status|priority|due_date",
                "filter_value": "value to filter by"
            }
        }

        IMPORTANT:
        1. NEVER return just the action type
        2. ALWAYS include all required fields for the chosen action
        3. Ensure the response matches exactly one of these structures
        4. All dates must be in YYYY-MM-DD format
        5. Priority must be one of: low, medium, high
        6. Status must be one of: pending, in_progress, completed
        """,
        input_payload=todo_action_payload,
        output_payload=todo_action_payload,
    )
