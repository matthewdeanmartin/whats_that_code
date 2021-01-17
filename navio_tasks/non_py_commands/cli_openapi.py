"""
Does swagger/openapi file parse
"""

import os
import shlex
import sys

from navio_tasks.cli_commands import config_pythonpath, execute, execute_get_text
from navio_tasks.output import say_and_exit
from navio_tasks.settings import IS_GITLAB, IS_JENKINS, PROJECT_NAME, VENV_SHELL
from navio_tasks.utils import inform


def do_openapi_check() -> None:
    """
    Does swagger/openapi file parse
    """
    if not os.path.exists(f"{PROJECT_NAME}/api.yaml"):
        inform("No api.yaml file, assuming this is not a microservice")
        # TODO: should be able to check all y?ml files and look at header.
        return

    command_text = (
        f"{VENV_SHELL} "
        "openapi-spec-validator"
        f" {PROJECT_NAME}/api.yaml".strip().replace("  ", " ")
    )
    inform(command_text)
    command = shlex.split(command_text)
    execute(*command)

    if IS_JENKINS or IS_GITLAB:
        inform("Jenkins/Gitlab and apistar don't work together, skipping")
        return

    command_text = (
        f"{VENV_SHELL} apistar validate "
        f"--path {PROJECT_NAME}/api.yaml "
        "--format openapi "
        "--encoding yaml".strip().replace("  ", " ")
    )
    inform(command_text)
    # subprocess.check_call(command.split(" "), shell=False)
    command = shlex.split(command_text)
    result = execute_get_text(command, ignore_error=True, env=config_pythonpath())
    if "OK" not in result and "2713" not in result and "✓" not in result:
        inform(result)
        say_and_exit("apistar didn't like this", "apistar")
        sys.exit(-1)
