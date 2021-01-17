"""
Lots of code gripes.
"""
import os
import shlex
import subprocess
import sys
from typing import List

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, config_pythonpath
from navio_tasks.output import say_and_exit
from navio_tasks.pure_reports.cli_pygount import total_loc
from navio_tasks.settings import (
    IS_DJANGO,
    IS_GITLAB,
    PROBLEMS_FOLDER,
    PROJECT_NAME,
    VENV_SHELL,
)
from navio_tasks.utils import inform


def do_lint(folder_type: str) -> str:
    """
    Execute pylint
    """
    # pylint: disable=too-many-locals
    check_command_exists("pylint")
    if folder_type == PROJECT_NAME:
        pylintrc = f"{settings.CONFIG_FOLDER}/.pylintrc"
        lint_output_file_name = f"{PROBLEMS_FOLDER}/lint.txt"
    else:
        pylintrc = f"{settings.CONFIG_FOLDER}/.pylintrc_{folder_type}"
        lint_output_file_name = f"{PROBLEMS_FOLDER}/lint_{folder_type}.txt"

    if os.path.isfile(lint_output_file_name):
        os.remove(lint_output_file_name)

    if IS_DJANGO:
        django_bits = "--load-plugins pylint_django "
    else:
        django_bits = ""

    # pylint: disable=pointless-string-statement
    command_text = (
        f"{VENV_SHELL} pylint {django_bits} " f"--rcfile={pylintrc} {folder_type} "
    )

    command_text += " "
    "--msg-template={path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"
    "".strip().replace("  ", " ")

    inform(command_text)
    command = shlex.split(command_text)

    with open(lint_output_file_name, "w") as outfile:
        env = config_pythonpath()
        subprocess.call(command, stdout=outfile, env=env)
    return lint_output_file_name


def evaluated_lint_results(
    lint_output_file_name: str,
    small_code_base_cut_off: int,
    maximum_lint: int,
    fatals: List[str],
) -> str:
    """Deciding if the lint is bad enough to fail
    Also treats certain errors as fatal even if under the maximum cutoff.
    """
    with open(lint_output_file_name) as file_handle:
        full_text = file_handle.read()
    lint_did_indeed_run = "Your code has been rated at" in full_text

    with open(lint_output_file_name) as file_handle:
        fatal_errors = sum(1 for line in file_handle if ": E" in line or ": F" in line)
        for fatal in fatals:
            for line in file_handle:
                if fatal in file_handle or ": E" in line or ": F" in line:
                    fatal_errors += 1

    if fatal_errors > 0:
        with open(lint_output_file_name) as file_handle:
            for line in file_handle:
                if "*************" in line:
                    continue
                if not line or not line.strip("\n "):
                    continue
                inform(line.strip("\n "))

        message = f"Fatal lint errors and possibly others, too : {fatal_errors}"
        if IS_GITLAB:
            with open(lint_output_file_name) as error_file:
                inform(error_file.read())
        say_and_exit(message, "lint")
        return message
    with open(lint_output_file_name) as lint_file_handle:
        for line in [
            line
            for line in lint_file_handle
            if not (
                "*************" in line
                or "---------------------" in line
                or "Your code has been rated at" in line
                or line == "\n"
            )
        ]:
            inform(line)

    if total_loc() > small_code_base_cut_off:
        cutoff = maximum_lint
    else:
        cutoff = 0
    with open(lint_output_file_name) as lint_file_handle:
        num_lines = sum(
            1
            for line in lint_file_handle
            if not (
                "*************" in line
                or "---------------------" in line
                or "Your code has been rated at" in line
                or line == "\n"
            )
        )
    if num_lines > cutoff:
        say_and_exit(f"Too many lines of lint : {num_lines}, max {cutoff}", "pylint")
        sys.exit(-1)
    with open(lint_output_file_name) as lint_file_handle:
        num_lines_all_output = sum(1 for _ in lint_file_handle)
    if (
        not lint_did_indeed_run
        and num_lines_all_output == 0
        and os.path.isfile(lint_output_file_name)
    ):
        # should always have at least 'found 0 errors' in output

        # force lint to re-run, because empty file will be missing
        os.remove(lint_output_file_name)
        say_and_exit(
            "No lint messages at all, did pylint fail to run or is it installed?",
            "pylint",
        )
        sys.exit(-1)

    return "pylint succeeded"
