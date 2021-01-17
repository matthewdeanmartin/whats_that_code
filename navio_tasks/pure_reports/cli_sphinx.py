"""
Generate docs based on rst.
"""
from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute_with_environment,
)
from navio_tasks.settings import VENV_SHELL
from navio_tasks.utils import inform


def do_docs() -> str:
    """
    Generate docs based on rst.
    """
    check_command_exists("make")

    my_env = config_pythonpath()
    command = f"{VENV_SHELL} make html".strip().replace("  ", " ")
    inform(command)
    execute_with_environment(command, env=my_env)
    return "Docs generated"
