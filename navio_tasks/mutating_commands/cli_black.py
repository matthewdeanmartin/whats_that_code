"""
Modifies code.
- Modified code will have to be checked in.

If code needs to be modified and we are on a build server, maybe break build.
"""

import shlex
import sys
from typing import Dict

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute,
    execute_get_text,
)
from navio_tasks.settings import IS_GITLAB, PROJECT_NAME, VENV_SHELL
from navio_tasks.system_info import is_windows, is_git_repo
from navio_tasks.utils import inform


def do_formatting(check: str, state: Dict[str, bool]) -> None:
    """
    Format with black - this will not modify code if check is --check
    """

    # check & format should be merged & use an arg
    # global FORMATTING_CHECK_DONE
    if state["check_already_done"]:
        inform("Formatting check says black will not reformat, so no need to repeat")
        return
    if sys.version_info < (3, 6):
        inform("Black doesn't work on python 2")
        return
    check_command_exists("black")

    command_text = f"{VENV_SHELL} black {PROJECT_NAME} {check}".strip().replace(
        "  ", " "
    )
    inform(command_text)
    command = shlex.split(command_text)
    if check:
        _ = execute(*command)
        state["check_already_done"] = True
        return
    result = execute_get_text(command, env=config_pythonpath())
    assert result
    changed = []
    for line in result.split("\n"):
        if "reformatted " in line:
            file = line[len("reformatted ") :].strip()
            changed.append(file)
    if not IS_GITLAB:
        if not is_git_repo("."):
            # don't need to git add anything because this isn't a git repo
            return
        for change in changed:
            if is_windows():
                change = change.replace("\\", "/")
            command_text = f"git add {change}"
            inform(command_text)
            command = shlex.split(command_text)
            execute(*command)
