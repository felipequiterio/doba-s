import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from llm.agent import Agent
from utils.log import get_custom_logger

logger = get_custom_logger("TODO AGENT")

TODO_FILE = "todo_list.json"


class Task(BaseModel):
    task_id: int
    task_description: str
    status: str = "pending"
    created_at: str = datetime.now().isoformat()


class TodoList(BaseModel):
    tasks: Dict[str, List[Task]] = {}


class TodoAgentData(BaseModel):
    name: str
    description: str
    system_prompt: str
    input_payload: Dict
    output_payload: Dict
    todo_list: TodoList


class TodoAgent(Agent):
    data: TodoAgentData

    def __init__(self):
        logger.info("Initializing TodoAgent")
        todo_list = self.load_todo_list()
        data = TodoAgentData(
            name="todo_agent",
            description="Manages the user's to-do list.",
            system_prompt="""
You are an intelligent assistant responsible for managing a user's to-do list. Your primary functions include adding, updating, viewing, and deleting tasks. Follow these guidelines for each action:

1. Adding a task:
   - Ensure the task description is clear and concise.
   - Assign a unique task ID.
   - Set the initial status as "pending".
   - Record the creation date and time.

2. Updating a task:
   - Locate the task by ID or description (case-insensitive).
   - Modify the specified fields (status or description).
   - Maintain the original creation date.

3. Viewing tasks:
   - Retrieve all tasks for the current date.
   - Present tasks in a clear, organized manner.

4. Deleting a task:
   - Locate the task by ID or description (case-insensitive).
   - Remove the task from the list.
   - Confirm the deletion.

For all actions:
- Provide clear feedback on the success or failure of the operation.
- In case of errors, offer specific error messages and potential solutions.
- Ensure all interactions maintain data integrity and consistency.

Your responses should be structured, informative, and user-friendly. Always confirm the action taken and provide the updated task information when applicable.
            """,
            input_payload=todo_payload,
            output_payload={},
            todo_list=todo_list,
        )
        super().__init__(
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            input_payload=data.input_payload,
            output_payload=data.output_payload,
            data=data,
        )

    def execute(self, arguments: Dict[str, Any]):
        logger.info(f"Executing TodoAgent with arguments: {arguments}")

        action = arguments.get("action")
        item = arguments.get("item", {})

        task_description = (
            item.get("task_description")
            or item.get("task_name")
            or item.get("task")
            or item.get("text")
        )
        task_id = item.get("task_id")
        status = "completed" if item.get("completed") else "pending"

        return self.manage_task(
            action, task_id=task_id, task_description=task_description, status=status
        )

    def manage_task(self, action, task_id=None, task_description=None, status=None):
        logger.info(f"Managing task with action: {action}")
        actions = {
            "add": lambda: self.add_task(task_description),
            "update": lambda: self.update_task(task_id, status, task_description),
            "delete": lambda: self.delete_task(task_id or task_description),
            "view": self.view_tasks,
        }

        action_function = actions.get(action)
        if action_function:
            result = action_function()
            logger.info(f"Task managed successfully: {result}")
            return {"success": True, "result": result}
        else:
            logger.error(f"Invalid action: {action}")
            return {"success": False, "error": f"Invalid action: {action}"}

    def add_task(self, task_description: str) -> Dict[str, Any]:
        if not task_description:
            return {
                "success": False,
                "error": "Task description is required for adding a task",
            }

        logger.info(f"Adding task to todo list: {task_description}")
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.data.todo_list.tasks:
            self.data.todo_list.tasks[today] = []

        task_id = len(self.data.todo_list.tasks[today]) + 1
        new_task = Task(task_id=task_id, task_description=task_description)
        self.data.todo_list.tasks[today].append(new_task)
        self.save_todo_list()
        return {"success": True, "result": new_task.dict()}

    def update_task(
        self,
        task_id: Optional[int],
        status: Optional[str],
        task_description: Optional[str],
    ) -> Dict[str, Any]:
        logger.info(
            f"Updating task: ID={task_id}, Status={status}, Description={task_description}"
        )
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.data.todo_list.tasks:
            for task in self.data.todo_list.tasks[today]:
                if (
                    task.task_id == task_id
                    or task.task_description.lower() == task_description.lower()
                ):
                    if status:
                        task.status = status
                    if task_description:
                        task.task_description = task_description
                    self.save_todo_list()
                    return {"success": True, "result": task.dict()}
        return {"success": False, "error": "Task not found"}

    def delete_task(self, identifier: Any) -> Dict[str, Any]:
        logger.info(f"Deleting task: {identifier}")
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.data.todo_list.tasks:
            tasks = self.data.todo_list.tasks[today]
            for i, task in enumerate(tasks):
                if (
                    task.task_id == identifier
                    or task.task_description.lower() == str(identifier).lower()
                ):
                    deleted_task = tasks.pop(i)
                    self.save_todo_list()
                    return {"success": True, "result": deleted_task.dict()}
        return {"success": False, "error": "Task not found"}

    def view_tasks(self) -> Dict[str, Any]:
        logger.info("Viewing tasks from todo list")
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = self.data.todo_list.tasks.get(today, [])
        return {"success": True, "result": [task.dict() for task in tasks]}

    def load_todo_list(self) -> TodoList:
        logger.info("Loading todo list")
        try:
            with open(TODO_FILE, "r") as file:
                data = json.load(file)
                return TodoList(**data)
        except FileNotFoundError:
            return TodoList()

    def save_todo_list(self):
        with open(TODO_FILE, "w") as file:
            json.dump(self.data.todo_list.dict(), file, indent=4)


def create_todo_agent():
    return TodoAgent()


todo_payload = {
    "type": "function",
    "function": {
        "name": "todo_agent",
        "description": "Manage a to-do list, including adding, deleting, updating items, and viewing the list.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "delete", "update", "view"],
                    "description": "The action to perform on the to-do list",
                },
                "item": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "The unique identifier of the task (for update and delete actions)",
                        },
                        "task_description": {
                            "type": "string",
                            "description": "The description of the task (for add and update actions)",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "completed"],
                            "description": "The status of the task (for update action)",
                        },
                    },
                    "required": ["task_description"],
                },
            },
            "required": ["action", "item"],
        },
    },
}
