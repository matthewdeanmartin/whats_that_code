"""
Pin deps
"""
import os

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import VENV_SHELL
from navio_tasks.utils import inform


def convert_pipenv_to_requirements(pipenv: bool) -> None:
    """
    Create requirement*.txt
    """
    if not pipenv:
        raise TypeError(
            "Can't pin dependencies this way, we are only converting "
            "pipfile to requirements.txt"
        )
    check_command_exists("pipenv_to_requirements")

    execute(
        *(
            f"{VENV_SHELL} pipenv_to_requirements "
            f"--dev-output {settings.CONFIG_FOLDER}/requirements-dev.txt "
            f"--output {settings.CONFIG_FOLDER}/requirements.txt".strip().split(" ")
        )
    )
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/requirements.txt"):
        inform(
            "Warning: no requirements.txt found, assuming it is because there are"
            "no external dependencies yet"
        )
    else:
        with open(f"{settings.CONFIG_FOLDER}/requirements.txt", "r+") as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if line.find("-e .") == -1:
                    file.write(line)
            file.truncate()

    with open(f"{settings.CONFIG_FOLDER}/requirements-dev.txt", "r+") as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if line.find("-e .") == -1:
                file.write(line)
        file.truncate()
