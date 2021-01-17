"""
Lines fo code counting
"""
import os
import shlex
import subprocess

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, prepinform_simple
from navio_tasks.output import say_and_exit
from navio_tasks.settings import REPORTS_FOLDER
from navio_tasks.utils import inform


def total_loc() -> int:
    """
    Get Lines of Code for app
    """
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
    # pylint: disable=bare-except
    try:
        with open(
            f"{settings.CONFIG_FOLDER}/.build_state/pygount_total_loc.txt"
        ) as file_handle:
            total_loc_value = file_handle.read()
    except:  # noqa: B001
        do_count_lines_of_code()
        with open(
            f"{settings.CONFIG_FOLDER}/.build_state/pygount_total_loc.txt"
        ) as file_handle:
            total_loc_value = file_handle.read()

    return int(total_loc_value)


def do_count_lines_of_code() -> None:
    """
    Scale failure cut offs based on Lines of Code
    """
    command_name = "pygount"
    check_command_exists(command_name)
    command_text = prepinform_simple(command_name)

    # keep out of src tree, causes extraneous change detections
    if not os.path.exists(f"{REPORTS_FOLDER}"):
        os.makedirs(f"{REPORTS_FOLDER}")
    output_file_name = f"{REPORTS_FOLDER}/line_counts.txt"
    command = shlex.split(command_text)
    with open(output_file_name, "w") as outfile:
        subprocess.call(command, stdout=outfile)

    with open(output_file_name) as file_handle:
        lines = sum(int(line.split("\t")[0]) for line in file_handle if line != "\n")

    total_loc_local = lines
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
    with open(
        f"{settings.CONFIG_FOLDER}/.build_state/pygount_total_loc.txt", "w+"
    ) as state_file:
        state_file.write(str(total_loc_local))

    inform(f"Lines of code: {total_loc_local}")
    if total_loc_local == 0:
        say_and_exit(
            "No code found to build or package. Maybe the PROJECT_NAME is wrong?",
            "lines of code",
        )
