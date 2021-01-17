"""
Security tool. Unsupported since 3.9
"""
import sys

from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple


def do_python_taint() -> str:
    """
    Security Checks
    """
    if sys.version_info.major == 3 and sys.version_info.minor > 8:
        # pyt only works with python <3.8
        return "skipping python taint"

    command = "pyt"
    check_command_exists(command)
    command = "pyt -r"
    command = prepinform_simple(command)
    execute(*(command.split(" ")))
    return "ok"
