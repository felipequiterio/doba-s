import os
import llm.query
import llm.task
from stream import sync
from dotenv import load_dotenv
import llm
from llm.initialize_agents import initialize_agents
from utils.log import get_custom_logger
from colorama import init, Fore, Back, Style

# Inicializa o colorama para funcionar em todos os sistemas operacionais
init()

logger = get_custom_logger("MAIN")

load_dotenv()
MODEL = os.getenv("MODEL")

agent_manager, agent_list = initialize_agents()


def print_separator():
    print(Fore.YELLOW + "=" * 80 + Style.RESET_ALL)


def print_run_header(run_number, message):
    print_separator()
    print(Fore.CYAN + f"RUN {run_number}".center(80) + Style.RESET_ALL)
    print(Fore.GREEN + f"Input: {message}" + Style.RESET_ALL)
    print_separator()


def print_result(result):
    if result["success"]:
        print(Fore.GREEN + "Task completed successfully:" + Style.RESET_ALL)
        print(Fore.WHITE + Back.GREEN + f"{result['result']}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Task failed:" + Style.RESET_ALL)
        print(Fore.WHITE + Back.RED + f"{result['error']}" + Style.RESET_ALL)


def run_agent(message):
    logger.info(f"Running agent with message: {message}")
    main_agent_payload = llm.query.route(message)
    main_agent = main_agent_payload["message"]["tool_calls"][0]["function"][
        "arguments"
    ]["agent"]
    logger.info(f"Main agent: {main_agent}")

    if main_agent == "conversational":
        sync(message)
    elif main_agent == "tool":
        task_object = llm.task.generate(message)
        results = llm.task.route(task_object, agent_manager)

        for result in results:
            print_result(result)


# Examples of usage
examples = [
    "Hello, can you add 'buy groceries' to my todo list?",
    "What tasks do I have on my todo list?",
    "Can you mark the task 'buy groceries' as completed?",
    "Please delete the task 'buy groceries' from my list",
    "How's the weather today?",
]

for i, example in enumerate(examples, 1):
    print_run_header(i, example)
    run_agent(example)
    print("\n")

print_separator()
print(Fore.CYAN + "All runs completed.".center(80) + Style.RESET_ALL)
print_separator()
