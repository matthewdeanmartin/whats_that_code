"""
Reformat code to use py3 patterns when possible
"""

import glob

from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import PROJECT_NAME, VENV_SHELL
from navio_tasks.utils import inform


def do_pyupgrade(is_interactive: bool, minimum_python: str) -> str:
    """Update syntax to most recent variety."""
    if not is_interactive:
        inform("Not an interactive session, skipping pyupgrade wihch changes files.")
        return "Skipping"
    command = "pyupgrade"
    check_command_exists(command)

    all_files = " ".join(
        f for f in glob.glob(f"{PROJECT_NAME}/**/*.py", recursive=True)
    )

    # as of 2021, still doesn't appear to support recursive globs natively.
    command = (
        f"{VENV_SHELL} pyupgrade "
        f"--{minimum_python}-plus "
        f"--exit-zero-even-if-changed {all_files}".strip().replace("  ", " ")
    )
    inform(command)
    execute(*(command.split(" ")))
    return f"{command} succeeded"
