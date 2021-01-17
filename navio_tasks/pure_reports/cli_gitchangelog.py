"""
Extract commit comments from git to a report. Makes for a lousy CHANGELOG.md
"""
import shlex

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute_get_text,
)
from navio_tasks.settings import VENV_SHELL
from navio_tasks.utils import inform


def do_gitchangelog() -> None:
    """
    Extract commit comments from git to a report. Makes for a lousy CHANGELOG.md
    """
    # TODO: this app has lots of features for cleaning up comments
    command_name = "gitchangelog"
    check_command_exists(command_name)

    command_text = f"{VENV_SHELL} {command_name}".strip().replace("  ", " ")
    inform(command_text)
    command = shlex.split(command_text)
    with open("ChangeLog", "w+") as change_log:
        result = execute_get_text(command, env=config_pythonpath()).replace("\r", "")
        change_log.write(result)
