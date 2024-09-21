from crewai import Crew, Task, Process
from dotenv import load_dotenv
import os

from agents.manager import agent as manager_agent
from agents.todo import agent as todo_agent
from llm import llm
from tasks.todo import handle_todo_list

load_dotenv()
os.environ["OPENAI_API_KEY"] = "NA"

def create_general_task():
    task = Task(
            description='Adicionar fazer a cama na todo list',
            expected_output="Status for the operation",
            agent = None
        )
    
    return task


    # Solicitar input do usuário
    # user_input = input("Digite a tarefa que deseja realizar (ou 'sair' para finalizar): ")
    
    # # Verificar se o usuário deseja sair do loop
    # if user_input.lower() == 'sair':
    #     break

# Criar a tarefa dinâmica
task = create_general_task()

# Criar a configuração do crew
crew = Crew(
    agents=[todo_agent],
    tasks=[task],
    process=Process.hierarchical,
    manager_agent=manager_agent,
    manager_llm=llm
)

# Iniciar o processo
result = crew.kickoff()
print(result)