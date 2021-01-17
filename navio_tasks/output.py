"""
Console output related
"""
import subprocess
import sys

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists
from navio_tasks.system_info import check_is_aws
from navio_tasks.utils import inform


def say_and_exit(message: str, source: str) -> None:
    """
    Audibly notify the developer that the build is
    done so that long builds wouldn't cause an attention problem
    """
    inform(f"{source}:{message}")
    if (
        settings.SPEAK_WHEN_BUILD_FAILS
        and settings.IS_INTERACTIVE
        and not check_is_aws()
    ):
        # TODO: check a profile option or something.
        if check_command_exists("say", throw_on_missing=False, exit_on_missing=False):
            subprocess.call(["say", message])
        elif check_command_exists(
            "wsay.exe", throw_on_missing=False, exit_on_missing=False
        ):
            subprocess.call(["wsay", message])
    sys.exit(-1)
