"""
Check yaml, but doesn't reformat it
"""
from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import PROJECT_NAME, VENV_SHELL
from navio_tasks.utils import inform


def do_yamllint() -> str:
    """
    Check yaml files for problems
    """
    command = "yamllint"
    check_command_exists(command)

    command = f"{VENV_SHELL} yamllint {PROJECT_NAME}".strip().replace("  ", " ")
    inform(command)
    execute(*(command.split(" ")))
    return "yamllint succeeded"
