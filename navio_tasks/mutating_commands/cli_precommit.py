"""
Precommit is a generic checker/build tool. It can contain a few or lots of
tools, many of them not python specific.
"""
import shlex
import sys

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute,
    execute_get_text,
)
from navio_tasks.output import say_and_exit
from navio_tasks.settings import VENV_SHELL
from navio_tasks.system_info import is_git_repo
from navio_tasks.utils import inform


def do_precommit(is_interactive: bool) -> None:
    """
    Build time execution of pre-commit checks. Modifies code so run before linter.
    """
    if not is_interactive:
        inform("Not running precommit because it changes files")
        return
    check_command_exists("pre-commit")

    if is_git_repo("."):
        # don't try to install because it isn't a git repo
        command_text = f"{VENV_SHELL} pre-commit install".strip().replace("  ", " ")
        inform(command_text)
        command = shlex.split(command_text)
        execute(*command)

    command_text = f"{VENV_SHELL} pre-commit run --all-files".strip().replace("  ", " ")
    inform(command_text)
    command = shlex.split(command_text)
    result = execute_get_text(command, ignore_error=True, env=config_pythonpath())
    assert result
    changed = []
    for line in result.split("\n"):
        if "changed " in line:
            file = line[len("reformatted ") :].strip()
            changed.append(file)
    if "FAILED" in result:
        inform(result)
        say_and_exit("Pre-commit Failed", "pre-commit")
        sys.exit(-1)

    if is_interactive:
        if not is_git_repo("."):
            # don't need to git add anything because this isn't a git repo
            return
        for change in changed:
            command_text = f"git add {change}"
            inform(command_text)
            # this breaks on windows!
            # command = shlex.split(command_text)
            execute(*command_text.split())
