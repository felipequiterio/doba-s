import os
import llm
import llm.task
import llm.query
from stream import stream
from typing import Dict, Any
from dotenv import load_dotenv
from llm.agent import AgentHandler
from utils.log import get_custom_logger
from colorama import init, Fore, Back, Style
from llm.initialize_agents import initialize_agents

init()

logger = get_custom_logger("MAIN")

load_dotenv()
MODEL = os.getenv("MODEL")

agent_manager, agent_list = initialize_agents()


def extract_main_agent(payload: Dict[str, Any]) -> str:
    """Extract the main agent from the routing payload."""
    return payload["message"]["tool_calls"][0]["function"]["arguments"]["agent"]


def handle_conversational_agent(message: str) -> None:
    """Handle messages routed to the conversational agent."""
    stream(message)


def handle_tool_agent(message: str, agent_manager: AgentHandler) -> None:
    """Handle messages routed to tool agents."""
    task_object = llm.task.generate(message, agent_list)
    results = llm.task.route(task_object, agent_manager)

    for result in results:
        print_result(result)


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


def run_agent(message: str, agent_manager: AgentHandler) -> None:
    logger.info(f"Processing message: {message}")

    main_agent_payload = llm.query.route(message)
    main_agent = main_agent_payload["agent"]
    logger.info(f"Routed to main agent: {main_agent}")

    if main_agent == "conversational":
        stream(message)

    elif main_agent == "tool":
        agent_list = agent_manager.get_list()
        task_list = llm.task.generate(message, agent_list)
        results = llm.task.route(task_list, agent_list)
        print_result(results)
    else:
        raise ValueError(f"Invalid agent type: {main_agent}")


# Examples of usage
examples = [
    "Hello, can you add 'buy groceries' to my todo list?",
    # "What tasks do I have on my todo list?",
    # "Can you mark the task 'buy groceries' as completed?",
    # "Please delete the task 'buy groceries' from my list",
    # "How's the weather today?",
]

for i, example in enumerate(examples, 1):
    print_run_header(i, example)
    run_agent(example, agent_manager)
    print("\n")

print_separator()
print(Fore.CYAN + "All runs completed.".center(80) + Style.RESET_ALL)
print_separator()
