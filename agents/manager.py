from crewai import Agent
from llm import llm
# Defina as ferramentas personalizadas que o agente pode usar
# Exemplo de ferramenta SerperDevTool

agent = Agent(
    role='Manager Agent',
    goal='Route queries to the appropriate agents or handle them directly',
    backstory="""
    You are the Manager Agent, responsible for coordinating the activities of other agents.
    Your role includes routing user queries to the appropriate specialized agents or handling 
    simple queries directly. You ensure that tasks are managed efficiently and that the user 
    receives accurate and timely responses. Your mission is to optimize task delegation and 
    maintain an organized workflow among all agents.
    """,
    # tools=[search_tool],  # Optional, add any specific tools the manager might use
    llm=llm,  # Optional
    # function_calling_llm=my_llm,  # Optional
    # max_iter=15,  # Optional
    # max_rpm=None, # Optional
    # max_execution_time=None, # Optional
    verbose=True,  # Optional
    allow_delegation=True,  # Optional
    # step_callback=my_intermediate_step_callback,  # Optional
    cache=True,  # Optional
    # system_template=my_system_template,  # Optional
    # prompt_template=my_prompt_template,  # Optional
    # response_template=my_response_template,  # Optional
    # config=my_config,  # Optional
    # crew=my_crew,  # Optional
    # tools_handler=my_tools_handler,  # Optional
    # cache_handler=my_cache_handler,  # Optional
    # callbacks=[callback1, callback2],  # Optional
    # agent_executor=my_agent_executor  # Optional
)

