from crewai import Task
from agents.todo import agent as todo_agent
from tools.todo import create_task, delete_task, update_task, read_tasks



handle_todo_list = Task(
        description='Handle operations in the user Todo list such as  read list, add items,remove items and update items ',
        expected_output = 'Status of the operation',
        agent = todo_agent,
        tools = [create_task, delete_task, update_task,read_tasks ]
    )
    
