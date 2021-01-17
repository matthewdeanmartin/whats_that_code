"""
This just makes sure that some human got a chance to say, "nope, not going to use
this because of license issues"
"""

import os

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple
from navio_tasks.utils import inform


def do_liccheck() -> str:
    """
    Make an explicit decision about license of referenced packages
    """

    check_command_exists("liccheck")
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/requirements.txt"):
        inform("No requirements.txt file, assuming we have no external deps")
        return "Skipping, not requirements.txt"
    command = (
        "liccheck "
        f"-r {settings.CONFIG_FOLDER}/requirements.txt "
        f"-s {settings.CONFIG_FOLDER}/.license_rules "
        "-l paranoid"
    )

    command = prepinform_simple(command, no_project=True)
    execute(*(command.split(" ")))
    return "liccheck succeeded"
