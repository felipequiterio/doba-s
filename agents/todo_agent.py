from pydantic import BaseModel


class TodoPayload(BaseModel):
    id: int
    task: str
    due_date: str
    priority: str  # high, medium, low
    status: str  # pending, completed


def list_tasks():
    pass


def list_tasks_by_status(status: str):
    pass


def list_tasks_by_priority(priority: str):
    pass


def list_tasks_by_due_date(due_date: str):
    pass


def add_task(task: TodoPayload):
    pass


def get_task(task: TodoPayload):
    pass


def update_task(task: TodoPayload):
    # Get tasks before update, make a call to llm before updating
    tasks = list_tasks(task.id)

    pass


def delete_task(id: int):
    pass
