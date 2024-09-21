from crewai import Agent
from tools.todo import create_task, delete_task, update_task, read_tasks
from llm import llm



agent = Agent(
    role='to-do list manager',
    goal='Handle the to-do list operations',
    backstory="""
    You're a dedicated assistant designed to help manage a to-do list.
    Your responsibilities include adding new tasks, listing all tasks, updating existing tasks, 
    and deleting tasks as required.
    """,
    tools=[create_task, delete_task, update_task,read_tasks ],  # Optional, defaults to an empty list
    llm=llm,  # Optional
#   function_calling_llm=my_llm,  # Optional
#   max_iter=15,  # Optional
#   max_rpm=None, # Optional
#   max_execution_time=None, # Optional
    verbose=True,  # Optional
#   allow_delegation=True,  # Optional
#   step_callback=my_intermediate_step_callback,  # Optional
#   cache=True,  # Optional
#   system_template=my_system_template,  # Optional
#   prompt_template=my_prompt_template,  # Optional
#   response_template=my_response_template,  # Optional
#   config=my_config,  # Optional
#   crew=my_crew,  # Optional
#   tools_handler=my_tools_handler,  # Optional
#   cache_handler=my_cache_handler,  # Optional
#   callbacks=[callback1, callback2],  # Optional
#   agent_executor=my_agent_executor  # Optional
)