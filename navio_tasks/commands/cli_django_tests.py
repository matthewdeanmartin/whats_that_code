"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
"""
import os

from navio_tasks.cli_commands import config_pythonpath, execute_with_environment
from navio_tasks.settings import PYTHON


# Legacy code. Don't use nose.
def do_django_tests() -> None:
    """
    manage.py tests
    """

    # check_command_exists("")
    if os.path.exists("manage.py"):
        do_django_tests_regardless()


def do_django_tests_regardless() -> None:
    """
    Extracted function to make easier to test this task
    """
    command = f"{PYTHON} manage.py test -v 2"
    my_env = config_pythonpath()
    execute_with_environment(command, env=my_env)
