import json
import os
from datetime import datetime
from typing import List
from time import time  # Importa a função time para o timer
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

# Definir o nome e caminho do arquivo
file_name = f"todo-list-{datetime.now().strftime('%Y-%m-%d')}.json"
file_path = os.path.join(os.path.dirname(__file__), file_name)

# Inicializar a lista de tarefas
todo_list = []

# Função para criar o arquivo, caso ele não exista
def create_file_if_not_exists():
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump([], file)

# Função para carregar a lista de tarefas
def load_todo_list():
    global todo_list
    start_time = time()  # Timer para o carregamento
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            todo_list = json.load(file)
    end_time = time()
    print(f"Time taken to load the todo list: {end_time - start_time:.4f} seconds")  # Exibe o tempo

# Função para salvar a lista de tarefas
def save_todo_list():
    start_time = time()  # Timer para o salvamento
    with open(file_path, 'w') as file:
        json.dump(todo_list, file, indent=4)
    end_time = time()
    print(f"Time taken to save the todo list: {end_time - start_time:.4f} seconds")  # Exibe o tempo

# Chamar a função para garantir que o arquivo existe
create_file_if_not_exists()

# Ferramenta para criar uma tarefa
@tool
def create_task(description: str, status='open') -> str:
    """Create a new task in the todo list.

    Args:
        description (str): The description of the task.
        status (str, optional): The status of the task. Defaults to 'open'.
    """
    global todo_list
    load_todo_list()  # Mede o tempo de carregamento da lista
    
    task = {
        'description': description,
        'status': status
    }
    todo_list.append(task)
    save_todo_list()  # Mede o tempo de salvamento da lista
    
    return 'Task created.'

# Ferramenta para ler todas as tarefas
@tool
def read_tasks() -> List[dict]:
    """Read all tasks from the todo list."""
    global todo_list
    load_todo_list()  # Mede o tempo de carregamento da lista
    return todo_list

# Ferramenta para atualizar uma tarefa existente
@tool
def update_task(task_index: int, description: str = None, status: str = None) -> str:
    """Update a task in the todo list.

    Args:
        task_index (int): The index of the task to update.
        description (str, optional): New description for the task.
        status (str, optional): New status for the task.
    """
    global todo_list
    load_todo_list()  # Mede o tempo de carregamento da lista
    
    if 0 <= task_index < len(todo_list):
        if description:
            todo_list[task_index]['description'] = description
        if status:
            todo_list[task_index]['status'] = status
        save_todo_list()  # Mede o tempo de salvamento da lista
        return 'Task updated.'
    else:
        raise IndexError('Task index out of range')

# Ferramenta para deletar uma tarefa
@tool
def delete_task(task_index: int) -> str:
    """Delete a task from the todo list.

    Args:
        task_index (int): The index of the task to delete.
    """
    global todo_list
    load_todo_list()  # Mede o tempo de carregamento da lista
    
    if 0 <= task_index < len(todo_list):
        todo_list.pop(task_index)
        save_todo_list()  # Mede o tempo de salvamento da lista
        return 'Task deleted.'
    else:
        raise IndexError('Task index out of range')

# Medir o tempo para instanciar o LLM e associar as ferramentas
start_llm_time = time()  # Timer para instanciar o ChatOllama

# Vincular as ferramentas ao modelo LLM
llm = ChatOllama(
    model="llama3.1:8b-instruct-q4_0",
    temperature=0,
).bind_tools([create_task, read_tasks, update_task, delete_task])

end_llm_time = time()  # Fim do timer para o ChatOllama
print(f"Time taken to instantiate LLM and bind tools: {end_llm_time - start_llm_time:.4f} seconds")  # Exibe o tempo

# Medir o tempo de execução do invoke
start_invoke_time = time()  # Começa o timer para o invoke

# Exemplo de chamada para o modelo invocando uma ferramenta
result = llm.invoke(
    "Please create a task with the description 'Go to school' and status 'open'."
)

end_invoke_time = time()  # Termina o timer para o invoke
invoke_time = end_invoke_time - start_invoke_time  # Calcula o tempo de execução

# Exibir o tempo de execução do invoke e o resultado
print(f"Time taken for invoke: {invoke_time:.4f} seconds")
print(result.tool_calls)
