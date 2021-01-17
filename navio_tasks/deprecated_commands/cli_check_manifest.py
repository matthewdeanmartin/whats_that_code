"""
This only matters if using setup.py/setup.cfg.
If using poetry + pyproject.toml you don't need setup.py, setup.cfg or MANIFEST.in

Better than using check-manifest, try to stop using setup.py
-----------
Only reports
Has option to generate MANIFEST.in if it doesn't exist.
Should break build on any issues, but has high false positive rate.
Expect a few issues all the time.
All issues should be addressable immediately.
"""

import os
import shlex
import subprocess
import sys
from typing import Dict

from navio_tasks.cli_commands import check_command_exists, config_pythonpath
from navio_tasks.output import say_and_exit
from navio_tasks.pure_reports.cli_pygount import total_loc
from navio_tasks.settings import (
    MAXIMUM_MANIFEST_ERRORS,
    PROBLEMS_FOLDER,
    SMALL_CODE_BASE_CUTOFF,
    VENV_SHELL,
)
from navio_tasks.utils import inform


def call_check_manifest_command(output_file_name: str, env: Dict[str, str]) -> None:
    """
    To allow for checking in multiple passes
    """
    check_command_exists("check-manifest")

    command_text = f"{VENV_SHELL} check-manifest".strip().replace("  ", " ")

    with open(output_file_name, "w") as outfile:
        inform(command_text)
        command = shlex.split(command_text)
        subprocess.call(command, stdout=outfile, env=env)


def do_check_manifest() -> str:
    """
    Require all files to be explicitly included/excluded from package
    """
    if not os.path.exists("setup.py") and not os.path.exists("setup.cfg"):
        inform("setup.py doesn't exists, not packaging.")
        return "Nope"
    env = config_pythonpath()
    output_file_name = f"{PROBLEMS_FOLDER}/manifest_errors.txt"
    call_check_manifest_command(output_file_name, env)

    with open(output_file_name) as outfile_reader:
        text = outfile_reader.read()

        inform(text)
        if not os.path.isfile("MANIFEST.in") and "no MANIFEST.in found" in text:
            command_text = f"{VENV_SHELL} check-manifest -c".strip().replace("  ", " ")
            command = shlex.split(command_text)
            subprocess.call(command, env=env)
            # inform("Had to create MANIFEST.in, please review and redo")
            call_check_manifest_command(output_file_name, env)

    if total_loc() > SMALL_CODE_BASE_CUTOFF:
        cutoff = 0
    else:
        cutoff = MAXIMUM_MANIFEST_ERRORS

    with open(output_file_name) as file_handle:
        num_lines = sum(
            1
            for line in file_handle
            if line
            and line.strip() != ""
            and "lists of files in version control and sdist match" not in line
        )
    if num_lines > cutoff:
        say_and_exit(
            f"Too many lines of manifest problems : {num_lines}, max {cutoff}",
            "check-manifest",
        )
        sys.exit(-1)
    return "manifest check succeeded"
