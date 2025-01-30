from colorama import Fore, Back, Style

# Initialize colorama
# init()


def print_separator():
    print(Fore.YELLOW + "=" * 80 + Style.RESET_ALL)


def print_run_header(run_number, message):
    print_separator()
    print(Fore.CYAN + f"RUN {run_number}".center(80) + Style.RESET_ALL)
    print(Fore.GREEN + f"Input: {message}" + Style.RESET_ALL)
    print_separator()


def print_result(result):
    if result["status"] == "success":
        print(Fore.GREEN + "Task completed successfully:" + Style.RESET_ALL)
        print(Fore.WHITE + Back.GREEN + f"{result['result']}" + Style.RESET_ALL)
    else:
        print(Fore.RED + "Task failed:" + Style.RESET_ALL)
        print(Fore.WHITE + Back.RED + f"{result['error']}" + Style.RESET_ALL)
