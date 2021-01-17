"""
Type checking. Hardest to fix, most likely to find a real bug.
"""
import subprocess
import sys
from typing import List

from navio_tasks.cli_commands import check_command_exists
from navio_tasks.output import say_and_exit
from navio_tasks.pure_reports.cli_pygount import total_loc

# Anything that feels like governance/policy should be in build.py
from navio_tasks.settings import PROBLEMS_FOLDER, PROJECT_NAME, VENV_SHELL
from navio_tasks.utils import inform


def do_mypy() -> str:
    """
    Are types ok?
    """
    check_command_exists("mypy")
    if sys.version_info < (3, 4):
        inform("Mypy doesn't work on python < 3.4")
        return "command is missing"
    command = (
        f"{VENV_SHELL} mypy {PROJECT_NAME} "
        "--ignore-missing-imports "
        "--strict".strip().replace("  ", " ")
    )
    inform(command)
    bash_process = subprocess.Popen(
        command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, _ = bash_process.communicate()  # wait
    mypy_file = f"{PROBLEMS_FOLDER}/all_mypy_errors.txt"
    with open(mypy_file, "w", encoding="utf-8") as out_file:
        out_file.write(out.decode())
    return mypy_file


def evaluated_mypy_results(
    mypy_file: str, small_code_base_cutoff: int, maximum_mypy: int, skips: List[str]
) -> str:
    """
    Decided if the mypy is bad enough to stop the build.
    """
    with open(mypy_file) as out_file:
        out = out_file.read()

    def contains_a_skip(line_value: str) -> bool:
        """
        Should this line be skipped
        """
        # skips is a closure
        for skip in skips:
            if skip in line_value or line_value.startswith(skip):
                return True
        return False

    actually_bad_lines: List[str] = []
    total_lines = 0
    with open(mypy_file, "w+") as lint_file:
        lines = out.split("\n")
        for line in lines:
            total_lines += 1
            if contains_a_skip(line):
                continue
            if not line.startswith(PROJECT_NAME):
                continue
            actually_bad_lines.append(line)
            lint_file.writelines([line])

    num_lines = len(actually_bad_lines)
    if total_loc() > small_code_base_cutoff:
        max_lines = maximum_mypy
    else:
        max_lines = 2  # off by 1 right now

    if num_lines > max_lines:
        for line in actually_bad_lines:
            inform(line)
        say_and_exit(f"Too many lines of mypy : {num_lines}, max {max_lines}", "mypy")
        sys.exit(-1)

    if num_lines == 0 and total_lines == 0:
        # should always have at least 'found 0 errors' in output
        say_and_exit(
            "No mypy warnings at all, did mypy fail to run or is it installed?", "mypy"
        )
        sys.exit(-1)
    return "mypy succeeded"
