import os
import json
from pydantic import BaseModel
from typing import Dict, Optional
from llm.invoke import ollama_invoke
from llm.agent import Agent, AgentTask
from utils.log import get_custom_logger

logger = get_custom_logger("Todo Agent")


todo_action_payload = {
    "name": "todo_action",
    "description": "Process a todo task action",
    "parameters": {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "The task description or query"},
            "expected_output": {
                "type": "string",
                "description": "Expected output format or result",
            },
            "action": {
                "type": "string",
                "enum": [
                    "add",
                    "update",
                    "delete",
                    "list",
                    "list_by_status",
                    "list_by_priority",
                    "list_by_due_date",
                ],
                "description": "The action to perform on the todo list",
            },
        },
        "required": ["task", "expected_output", "action"],
    },
}


todo_task_payload = {
    "name": "todo_task",
    "description": "Manage todo list tasks",
    "parameters": {
        "type": "object",
        "properties": {
            "task_object": {
                "type": "object",
                "description": "A todo task with all required fields including the action to perform",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Task ID (use 0 for new tasks, must be an integer)",
                        "default": 0,
                    },
                    "user_action": {
                        "type": "string",
                        "enum": ["add", "update", "delete", "list"],
                        "description": "The action to perform on the todo list (REQUIRED)",
                    },
                    "task": {
                        "type": "string",
                        "description": "Description of the task",
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Due date in YYYY-MM-DD format",
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "default": "medium",
                        "description": "Priority level of the task",
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "default": "pending",
                        "description": "Current status of the task",
                    },
                },
                "required": ["user_action", "task"],
            }
        },
        "required": ["task_object"],
    },
}


action_handler = {
    "add": lambda item: add_task(item),
    "update": lambda item: update_task(item),
    "delete": lambda item: delete_task(item.id),
    "list": lambda _: list_tasks(),
    "list_by_status": lambda item: list_tasks_by_status(item.status),
    "list_by_priority": lambda item: list_tasks_by_priority(item.priority),
    "list_by_due_date": lambda item: list_tasks_by_due_date(item.due_date),
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
        todo_task = ollama_invoke(
            system_message=self.system_prompt,
            user_message=agent_task.task,
            payload=todo_task_payload,
        )

        logger.info(f"Todo Agent RESPONSE:\n {json.dumps(todo_task, indent=2)}")

        # Handle both response formats
        task_data = todo_task.get("task_object", todo_task)
        action = task_data.get(
            "user_action", "list"
        )  # Default to list if not specified
        logger.info(f"Todo Agent action: {action}")

        # Special handling for list action
        if action == "list":
            return action_handler[action](None)  # Pass None as unused parameter

        # For other actions, create TodoPayload
        todo_item = TodoPayload(
            id=task_data.get("id", 0),
            task=task_data.get("task", ""),
            due_date=task_data.get("due_date", ""),
            priority=task_data.get("priority", "medium"),
            status=task_data.get("status", "pending"),
        )

        if action not in action_handler:
            raise ValueError(f"Unknown action: {action}")

        result = action_handler[action](todo_item)
        result["action"] = action
        return result


class TodoPayload(BaseModel):
    id: int
    task: str
    due_date: str
    priority: str  # high, medium, low
    status: str  # pending, completed


def _load_tasks():
    try:
        with open("todo_list.json", "r") as f:
            content = f.read().strip()
            if not content:  # File is empty
                return {"tasks": []}
            data = json.loads(content)
            tasks = data.get("tasks", [])

            # Create a new list instead of modifying during iteration
            normalized_tasks = []
            for i, task in enumerate(tasks):
                if isinstance(task, str):
                    normalized_tasks.append(
                        {
                            "id": i + 1,
                            "task": task,
                            "due_date": "",
                            "priority": "medium",
                            "status": "pending",
                        }
                    )
                else:
                    task_copy = task.copy()
                    if isinstance(task_copy.get("id"), str):
                        task_copy["id"] = int(task_copy["id"])
                    normalized_tasks.append(task_copy)

            return {"tasks": normalized_tasks}
    except (FileNotFoundError, json.JSONDecodeError):
        # Create the file with an empty task list
        empty_data = {"tasks": []}
        with open("todo_list.json", "w") as f:
            json.dump(empty_data, f, indent=4)
        return empty_data


def _save_tasks(tasks):
    with open("todo_list.json", "w") as f:
        json.dump(tasks, f, indent=4)


def add_task(task: TodoPayload):
    data = _load_tasks()
    tasks = data.get("tasks", [])

    if task.id == 0:
        existing_ids = [t["id"] for t in tasks if isinstance(t, dict)]
        task.id = max(existing_ids, default=0) + 1

    task_dict = task.model_dump()
    task_dict["id"] = int(task_dict["id"])  # Ensure ID is integer

    if not task_dict["priority"]:
        task_dict["priority"] = "medium"
    if not task_dict["status"]:
        task_dict["status"] = "pending"
    if not task_dict["due_date"]:
        task_dict["due_date"] = ""

    tasks.append(task_dict)
    data["tasks"] = tasks
    _save_tasks(data)
    return {
        "status": "success",
        "message": "Task added successfully",
        "data": [task_dict],
    }


def update_task(task: TodoPayload):
    data = _load_tasks()

    for i, existing_task in enumerate(data["tasks"]):
        if existing_task["id"] == task.id:
            data["tasks"][i] = task.model_dump()
            _save_tasks(data)
            return {
                "status": "success",
                "message": "Task updated successfully",
                "data": [task.model_dump()],
            }

    raise ValueError(f"Task with id {task.id} not found")


def delete_task(id: int):
    data = _load_tasks()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != id]
    _save_tasks(data)
    return {
        "status": "success",
        "message": f"Task {id} deleted successfully",
        "data": [],
    }


def list_tasks():
    data = _load_tasks()
    tasks = [TodoPayload(**task) for task in data["tasks"]]
    return {
        "status": "success",
        "message": "Retrieved all tasks",
        "data": [t.model_dump() for t in tasks],
    }


def list_tasks_by_status(status: str):
    tasks = [TodoPayload(**task) for task in _load_tasks()["tasks"]]
    filtered_tasks = [task for task in tasks if task.status == status]
    return {
        "status": "success",
        "message": f"Retrieved tasks with status: {status}",
        "data": [t.model_dump() for t in filtered_tasks],
    }


def list_tasks_by_priority(priority: str):
    tasks = [TodoPayload(**task) for task in _load_tasks()["tasks"]]
    filtered_tasks = [task for task in tasks if task.priority == priority]
    return {
        "status": "success",
        "message": f"Retrieved tasks with priority: {priority}",
        "data": [t.model_dump() for t in filtered_tasks],
    }


def list_tasks_by_due_date(due_date: str):
    tasks = [TodoPayload(**task) for task in _load_tasks()["tasks"]]
    filtered_tasks = [task for task in tasks if task.due_date == due_date]
    return {
        "status": "success",
        "message": f"Retrieved tasks with due date: {due_date}",
        "data": [t.model_dump() for t in filtered_tasks],
    }


def get_task(task_id: int) -> Optional[TodoPayload]:
    tasks = list_tasks()
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def create_todo_agent() -> TodoAgent:
    """Returns an instance of the TodoAgent class."""
    return TodoAgent(
        name="TodoAgent",
        description="Agent to manage todo list",
        system_prompt="""You are a todo list manager that MUST ALWAYS include a user_action in your responses.

        For every request, you must:
        1. Determine the appropriate action (add/update/delete/list)
        2. Include this action in the response as 'user_action'
        3. Provide all required task details

        When adding or updating tasks:
        - Assign a unique ID to new tasks
        - Validate that required fields are provided
        - Maintain data consistency

        Provide clear confirmations for all actions performed and format the output according to the expected structure.

        IMPORTANT: Always include a 'user_action' field in your response, which must be one of: 
        - 'add' for new tasks
        - 'update' for modifying existing tasks
        - 'delete' for removing tasks
        - 'list' for viewing tasks

        For every request, you must:
        
        1. Determine the appropriate action (add/update/delete/list)
        2. Include this action in the response as 'user_action'
        3. Provide all required task details

        Example response format:
        {
        "task_object": {
            "user_action": "add",  <- THIS FIELD IS MANDATORY
            "task": "Buy groceries",
            "id": 0,
            "due_date": "2024-03-20",
            "priority": "medium",
            "status": "pending"
        }
        }

        """,
        input_payload=todo_task_payload,
        output_payload=todo_task_payload,
    )
