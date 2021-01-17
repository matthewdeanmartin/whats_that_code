"""
Install dependencies so that build has a chance of succeeding.
"""
import os
import shlex

from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.utils import inform


def do_dependency_installs(pipenv: bool, poetry: bool, pip: bool) -> None:
    """Catch up with missing deps"""
    if pipenv:
        check_command_exists("pipenv")
        command_text = "pipenv install --dev --skip-lock"
        inform(command_text)
        command = shlex.split(command_text)
        execute(*command)
    elif poetry:
        check_command_exists("poetry")
        command_text = "poetry install"
        inform(command_text)
        command = shlex.split(command_text)
        execute(*command)
    elif pip:
        # TODO: move code to deprecated section?
        # TODO: Check for poetry.
        if os.path.exists("Pipfile"):
            raise TypeError("Found Pipfile, settings imply we aren't using Pipenv.")
        if os.path.exists("requirements.txt"):
            command_text = "pip install -r requirements.txt"
            inform(command_text)
            command = shlex.split(command_text)
            execute(*command)
        else:
            inform("no requirements.txt file yet, can't install dependencies")

        if os.path.exists("requirements-dev.txt"):
            command_text = "pip install -r requirements-dev.txt"
            inform(command_text)
            command = shlex.split(command_text)
            execute(*command)
        else:
            inform("no requirements-dev.txt file yet, can't install dependencies")
    else:
        inform("VENV not previously activated, won't attempt to catch up on installs")
