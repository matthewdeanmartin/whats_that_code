"""
Dead Code
"""
import shlex
import subprocess
import sys

from navio_tasks.cli_commands import check_command_exists, config_pythonpath
from navio_tasks.output import say_and_exit
from navio_tasks.pure_reports.cli_pygount import total_loc
from navio_tasks.settings import (
    MAXIMUM_DEAD_CODE,
    PROBLEMS_FOLDER,
    PROJECT_NAME,
    SMALL_CODE_BASE_CUTOFF,
    VENV_SHELL,
)
from navio_tasks.utils import inform


def do_vulture() -> str:
    """
    This also finds code you are working on today!
    """

    check_command_exists("vulture")

    # TODO: check if whitelist.py exists?
    command_text = f"{VENV_SHELL} vulture {PROJECT_NAME} whitelist.py"
    command_text = command_text.strip().replace("  ", " ")
    inform(command_text)
    command = shlex.split(command_text)

    output_file_name = f"{PROBLEMS_FOLDER}/dead_code.txt"
    with open(output_file_name, "w") as outfile:
        env = config_pythonpath()
        subprocess.call(command, stdout=outfile, env=env)

    if total_loc() > SMALL_CODE_BASE_CUTOFF:
        cutoff = MAXIMUM_DEAD_CODE
    else:
        cutoff = 0

    with open(output_file_name) as file_handle:
        num_lines = sum(1 for line in file_handle if line)
    if num_lines > cutoff:
        say_and_exit(
            f"Too many lines of dead code : {num_lines}, max {cutoff}", "vulture"
        )
        sys.exit(-1)
    return "dead-code (vulture) succeeded"
