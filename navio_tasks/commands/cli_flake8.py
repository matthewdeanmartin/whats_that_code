"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
-------
Rarely more than 1 or two issues if you have already worked pylint.
"""

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple


def do_flake8() -> str:
    """
    Flake8 Checks
    """
    command = "flake8"
    check_command_exists(command)
    command_text = f"flake8 --config {settings.CONFIG_FOLDER}/.flake8"
    command_text = prepinform_simple(command_text)
    execute(*(command_text.split(" ")))
    return "flake 8 succeeded"
