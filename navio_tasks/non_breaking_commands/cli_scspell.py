"""
Spell check. Most work for something that doesn't change application behavior.
"""

import os
import shlex

from navio_tasks import settings as settings
from navio_tasks.cli_commands import config_pythonpath, execute_get_text
from navio_tasks.settings import PROBLEMS_FOLDER, PROJECT_NAME, VENV_SHELL
from navio_tasks.utils import inform


def do_spell_check() -> None:
    """
    Check spelling using scspell (pip install scspell3k)
    """
    # tool can't recurse through files
    # tool returns a hard to parse format
    # tool has a really cumbersome way of adding values to dictionary
    walk_dir = PROJECT_NAME
    files_to_check = []
    inform(walk_dir)
    for root, _, files in os.walk(walk_dir):
        if "pycache" in root:
            continue
        for file in files:
            inform(root + "/" + file)
            if file.endswith(".py"):
                files_to_check.append(root + "/" + file)

    files_to_check_string = " ".join(files_to_check)
    command_text = (
        f"{VENV_SHELL} scspell --report-only "
        "--override-dictionary=spelling_dictionary.txt "
        f"--use-builtin-base-dict {files_to_check_string}".strip().replace("  ", " ")
    )
    inform(command_text)
    command = shlex.split(command_text)
    result = execute_get_text(command, ignore_error=True, env=config_pythonpath())
    with open(f"{PROBLEMS_FOLDER}/spelling.txt", "w+") as outfile:
        outfile.write(
            "\n".join(
                [
                    row
                    for row in result.replace("\r", "").split("\n")
                    if "dictionary" in row
                ]
            )
        )

    def read_file() -> None:
        with open(f"{settings.CONFIG_FOLDER}/spelling_dictionary.txt") as reading_file:
            reading_result = reading_file.read()
            inform(
                "\n".join(
                    [row for row in reading_result.split("\n") if "dictionary" in row]
                )
            )

    read_file()
