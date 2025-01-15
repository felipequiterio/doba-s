import os
import llm
import llm.task
import llm.query
from llm.stream import stream
from dotenv import load_dotenv
from llm.agent import AgentHandler
from utils.log import get_custom_logger
from colorama import init, Fore, Back, Style
from llm.initialize_agents import initialize_agents

# Initialize colorama
init()

# Initialize logging
logger = get_custom_logger("MAIN")

# Load environment variables
load_dotenv()
MODEL = os.getenv("MODEL")

# Initialize agents
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


def run_agent(message: str, agent_manager: AgentHandler) -> None:
    logger.info(f"Processing message: {message}")

    # Determine if message should be handled conversationally or by a tool
    query_route = llm.query.route(message)
    agent_type = query_route["agent"]
    logger.info(f"Message routed to {agent_type} agent")

    match agent_type:
        case "conversational":
            # Handle conversational messages by streaming response
            stream(message)

        case "tool":
            # Handle tool requests by generating and routing specific tasks
            available_agents = agent_manager.get_list()
            tasks = llm.task.generate(message, available_agents)
            results = llm.task.route(tasks, available_agents)
            print_result(results)

        case _:
            raise ValueError(f"Invalid agent type: {agent_type}")


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
