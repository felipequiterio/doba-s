import json
import os
from datetime import datetime
from crewai_tools import tool
from utils.log import get_custom_logger

file_name = f"todo-list-{datetime.now().strftime('%Y-%m-%d')}.json"
file_path = os.path.join(os.path.dirname(__file__), file_name)
todo_list = []

logger = get_custom_logger('TOOLS TO-DO')

def create_file_if_not_exists():
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            logger.info(f'Creating file: {file_name} at {file_path}')
            json.dump([], file)


def load_todo_list():
    global todo_list
    if os.path.exists(file_name):
        with open(file_path, 'r') as file:
            todo_list = json.load(file)

def save_todo_list():
    with open(file_name, 'w') as file:
        json.dump(todo_list, file, indent=4)

create_file_if_not_exists()

@tool("Create item")
def create_task(description: str, status='open'):
    """
    This tool is used to create an item in the todo list.
    Default status is 'open', just change if requested. 
    Status options are open, in progress and closed.
    """
    global todo_list
    
    load_todo_list()
    
    task = {
        'description': description,
        'status': status
    }
    todo_list.append(task)
    save_todo_list()
    return 'Task created.'

@tool("Read items list")
def read_tasks():
    """
    This tool is used to read all items and status from the todo list.
    """
    global todo_list
    return todo_list

@tool("Update item")
def update_task(task_index, description=None, status=None):
    """
    Tool used to update a item based on its index, useful after reading the item list.
    """
    global todo_list
    if 0 <= task_index < len(todo_list):
        if description:
            todo_list[task_index]['description'] = description
        if status:
            todo_list[task_index]['status'] = status
        save_todo_list()
        return 'Task updated.'
    else:
        raise IndexError('Task index out of range')

@tool("Delete item")
def delete_task(task_index):
    """
    This tool is used to delete a item based on its index.
    """
    global todo_list
    if 0 <= task_index < len(todo_list):
        removed_task = todo_list.pop(task_index)
        save_todo_list()
        return 'Task deleted'
    else:
        raise IndexError('Task index out of range')
