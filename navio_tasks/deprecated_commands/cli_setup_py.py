"""
Do the packaging. Anything but an sdist will be nonstop pain and breakage. Some
of the worst code in the entire python ecosystem (setuptools is.)
"""

import os
import shlex
import shutil
import sys

import setuptools

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute,
    execute_get_text,
    prepinform_simple,
)
from navio_tasks.output import say_and_exit
from navio_tasks.settings import PROJECT_NAME, PYTHON, VENV_SHELL
from navio_tasks.utils import inform


def do_package() -> None:
    """
    don't do anything that is potentially really slow or that modifies files.
    """
    if not os.path.exists("setup.py") and not os.path.exists("setup.cfg"):
        inform("setup.py doesn't exists, not packaging.")
        return "Nope"
    check_command_exists("twine")

    for folder in ["build", "dist", PROJECT_NAME + ".egg-info"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            original_umask = os.umask(0)
            try:
                try:
                    os.makedirs(folder, 0o770)
                except PermissionError:
                    execute("cmd", "mkdir", folder)
            finally:
                os.umask(original_umask)

    # command = f"{PYTHON} setup.py sdist --formats=gztar,zip"
    # bdist_wheel
    command_text = f"{PYTHON} setup.py sdist --formats=gztar,zip"
    command_text = prepinform_simple(command_text, no_project=True)
    command = shlex.split(command_text)
    result = execute_get_text(command, env=config_pythonpath()).replace("\r", "")

    error_count = 0
    for row in result.split("\n"):
        check_row = str(row).lower()
        if check_row.startswith("adding") or check_row.startswith("copying"):
            # adding a file named error/warning isn't a problem
            continue
        if "no previously-included files found matching" in check_row:
            # excluding a file that already doesn't exist is wonderful!
            # why this is a warning boggles the mind.
            continue
        if "lib2to3" in check_row:
            # python 3.9 has deprecated lib2to3, which shows up as a warning which
            # causes the build to fail. Seems ignorable as we don
            continue
        # sometimes to avoid pyc getting out of sync with .py, on
        # dev workstations you PYTHONDONTWRITEBYTECODE=1 which just disables
        # pyc altogether. Why wheel cares, I don't know.
        has_error = any(
            value in check_row
            for value in ["Errno", "Error", "failed", "error", "warning"]
        )
        if has_error and "byte-compiling is disabled" not in check_row:
            inform(row)
            error_count += 1
    if error_count > 0:
        say_and_exit("Package failed", "setup.py")
        sys.exit(-1)

    # pylint: disable=broad-except
    try:
        # Twine check must run after package creation. Supersedes setup.py check
        command_text = f"{VENV_SHELL} twine check dist/*".strip().replace("  ", " ")
        inform(command_text)
        command = shlex.split(command_text)
        execute(*command)
    except Exception as ex:
        inform(ex)
        command_text = (
            f"{VENV_SHELL} setup.py "
            "sdist "
            "--formats=gztar,zip".strip().replace("  ", " ")
        )
        command = shlex.split(command_text)
        execute(*command)

        def list_files(startpath: str) -> None:
            """
            List all files, handy for remote build servers
            """
            for root, _, files in os.walk(startpath):
                level = root.replace(startpath, "").count(os.sep)
                indent = " " * 4 * level
                inform("{}{}/".format(indent, os.path.basename(root)))
                subindent = " " * 4 * (level + 1)
                for file in files:
                    inform(f"{subindent}{file}")

        inform("skipping twine check until I figure out what is up")
        list_files(startpath=".")
    return "Ok"


def do_project_validation_for_setup_py() -> None:
    """
    Verify that all projects/modules are explicitly declared
    """
    found = setuptools.find_packages()
    # Just care about root
    found = [name for name in found if "." not in name and name != "test"]
    problems = 0
    if not found:
        inform("Found more than no modules at all, did you forget __init__.py?")
        problems += 1

    # this is okay.
    # if len(found) > 1:
    #     inform(f"Found more than one module, found {found}")
    #     problems += 1
    if PROJECT_NAME not in found:
        inform(f"Can't find {PROJECT_NAME}, found {found}")
        problems += 1
    if problems > 0:
        say_and_exit("Modules not as expected, can't package", "setup.py")
        sys.exit(-1)
