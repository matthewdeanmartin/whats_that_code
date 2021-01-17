"""
Check if metadata stuff in setup.py is filled in sensibly
"""
import os

from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import VENV_SHELL
from navio_tasks.utils import inform


def do_pyroma() -> str:
    """
    Check package goodness (essentially lints setup.py)
    """
    if os.path.exists("setup.py") or os.path.exists("setup.cfg"):
        return do_pyroma_regardless()
    return "Skipped, no setup.py/setup.cfg"


def do_pyroma_regardless() -> str:
    """
    Check package goodness (essentially lints setup.py)
    """
    if not os.path.exists("setup.py") and not os.path.exists("setup.cfg"):
        inform("setup.py doesn't exists, not packaging.")
        return "Nope"
    command = "pyroma"
    check_command_exists(command)
    command = f"{VENV_SHELL} pyroma --directory --min=8 .".strip().replace("  ", " ")
    inform(command)
    execute(*(command.split(" ")))
    return "pyroma succeeded"
