"""
See if everything works with python 3.8 and upcoming libraries
"""
import shlex

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import VENV_SHELL
from navio_tasks.utils import inform


def do_tox() -> str:
    """
    See if everything works with python 3.8 and upcoming libraries
    """
    # If tox fails the build with 3.8 or some future library, that means
    # we can't migrate to 3.8 yet, or that we should stay with currently pinned
    # libraries. We should fail the overall build.
    #
    # Because we control our python version we don't have to support cross ver
    # compatibility, i.e. we are not supporting 2.7 & 3.x!
    if settings.TOX_ACTIVE:
        # this happens when testing the build script itself.
        return "tox already, not nesting"
    command_name = "tox"
    check_command_exists(command_name)

    command_text = f"{VENV_SHELL} {command_name}".strip().replace("  ", " ")
    inform(command_text)
    command = shlex.split(command_text)
    execute(*command)
    return "tox succeeded"
