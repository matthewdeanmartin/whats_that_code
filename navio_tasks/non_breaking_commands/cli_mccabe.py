"""
Complexity reports
"""

import shlex

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple
from navio_tasks.settings import COMPLEXITY_CUT_OFF


def do_mccabe() -> str:
    """
    Complexity Checker
    """

    check_command_exists("flake8")  # yes, flake8, this is a plug in.
    # mccabe doesn't have a direct way to run it

    command_text = (
        f"flake8 --max-complexity {COMPLEXITY_CUT_OFF} "
        f"--config {settings.CONFIG_FOLDER}/.flake8"
    )
    command_text = prepinform_simple(command_text)
    command = shlex.split(command_text)
    execute(*command)
    return "mccabe succeeded"
