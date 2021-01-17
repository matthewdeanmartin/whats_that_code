"""
Generic tools for handling shell commands, as opposed to commands that
can be executed via `import tool`
"""
import io
import os
import re
import shlex
import shutil
import subprocess
import sys
from contextlib import redirect_stderr, redirect_stdout
from typing import Dict, Iterable, List, Optional, Tuple

import psutil

from navio_tasks import settings as settings
from navio_tasks.settings import PROJECT_NAME, VENV_SHELL
from navio_tasks.system_info import is_powershell
from navio_tasks.utils import inform


def config_pythonpath() -> Dict[str, str]:
    """
    Add to PYTHONPATH
    """
    my_env = {
        "PYTHONIOENCODING": "utf-8",
        "LC_ALL": "en_US.UTF-8",
        "LANG": "en_US.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "",
    }
    for key, value in os.environ.items():
        my_env[key] = value
    my_env["PYTHONPATH"] = my_env.get("PYTHONPATH", "")  # + VENDOR_LIBS
    return my_env


def is_cmd_exe() -> bool:
    """
    Check if parent process or other ancestor process is cmd
    """
    # ref https://stackoverflow.com/a/55598796/33264
    # Get the parent process name.
    try:
        process_name = psutil.Process(os.getppid()).name()
        grand_process_name = psutil.Process(os.getppid()).parent().name()
        # pylint: disable=bare-except, broad-except
        try:
            great_grand_process_name = (
                psutil.Process(os.getppid()).parent().parent().name()
            )
        except:  # noqa: B001
            great_grand_process_name = "No great grandparent"

        inform(process_name, grand_process_name, great_grand_process_name)
        is_that_shell = bool(re.fullmatch("cmd|cmd.exe", process_name))
        if not is_that_shell:
            is_that_shell = bool(re.fullmatch("cmd|cmd.exe", grand_process_name))
        if not is_that_shell:
            is_that_shell = bool(re.fullmatch("cmd|cmd.exe", great_grand_process_name))
    except psutil.NoSuchProcess:
        inform("Can't tell if this is cmd.exe, assuming not.")
        is_that_shell = False
    return is_that_shell


def check_command_exists(
    command: str, throw_on_missing: bool = False, exit_on_missing: bool = True
) -> bool:
    """
    Check if exists by a variety of methods that vary by shell

    # can this be replaced with shutil.which?
    """

    if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
    state_file = f"{settings.CONFIG_FOLDER}/.build_state/exists_" + command + ".txt"
    if os.path.exists(state_file):
        return True

    # when I originally wrote this function, I didn't know about shutil.which
    # if it performs well across many OSs, then we can phase out the rest.
    if shutil.which(command):
        already_found(command)
        return True
    venv_shell = [_ for _ in VENV_SHELL.split(" ") if _ != ""]

    # Build command & print. Must do here or the print gets redirected!
    # these commands lack a --version.
    if command in ["pyroma", "liccheck", "pipenv_to_requirements", "pyupgrade", "pyt"]:
        # will fail unless bash shell
        if is_powershell():
            cmd = venv_shell + ["powershell", "get-command", command]
        else:
            cmd = venv_shell + ["which", command]
    else:
        cmd = venv_shell + [command, "--version"]

    # pylint: disable=broad-except
    try:
        with io.StringIO() as buf, io.StringIO() as buf2, redirect_stdout(
            buf
        ), redirect_stderr(buf2):
            # execute command built up above.
            _ = subprocess.check_output(cmd)
            output = buf.getvalue()
            output2 = buf2.getvalue()
            inform(output, output2)
            if "not recognized" in output or "not recognized" in output2:
                inform(f"Got error checking if {command} exists")
                if throw_on_missing:
                    raise TypeError("Can't find command")
                if exit_on_missing:
                    sys.exit(-1)
                return False
            already_found(command)
    except OSError as os_error:
        inform(os_error)
        inform(f"Got error checking if {command} exists")
        if throw_on_missing:
            raise
        if exit_on_missing:
            sys.exit(-1)
        return False
    # pylint: disable=broad-except
    except Exception as ex:
        inform("Other error")
        inform(ex)
        inform(f"Got error checking if {command} exists")
        if throw_on_missing:
            raise
        if exit_on_missing:
            sys.exit(-1)
        return False
    return True


def already_found(command: str) -> None:
    """Check if we already checked if this command exists."""
    with open(
        f"{settings.CONFIG_FOLDER}/.build_state/exists_" + command + ".txt", "w+"
    ) as handle:
        handle.write("OK")


def prepinform_simple(command: str, no_project: bool = False) -> str:
    """
    Deal with simple command that only takes project name as arg
    """
    if no_project:
        command = f"{VENV_SHELL} {command}".strip().replace("  ", " ")
    else:
        command = f"{VENV_SHELL} {command} {PROJECT_NAME}".strip().replace("  ", " ")
    inform(command)
    return command


def execute_get_text(
    command: List[str],
    ignore_error: bool = False,
    # shell: bool = True, # causes cross plat probs, security warnings, etc.
    env: Optional[Dict[str, str]] = None,
) -> str:
    """
    Execute shell command and return stdout txt
    """
    if env is None:
        env = {}

    completed = None
    try:
        completed = subprocess.run(
            command,
            check=not ignore_error,
            # shell=shell, # causes cross plat probs, security warnings, etc.
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
    except subprocess.CalledProcessError:
        if ignore_error and completed:
            return completed.stdout.decode("utf-8") + completed.stderr.decode("utf-8")
        raise
    else:
        return completed.stdout.decode("utf-8") + completed.stderr.decode("utf-8")


# from pynt.contrib
def execute(script: str, *args: Iterable[str]) -> int:
    """
    Executes a command through the shell. Spaces should breakup the args.
    Usage: execute('grep', 'TODO', '*')
    """

    popen_args = [script] + list(args)
    # pylint: disable=broad-except
    try:
        return subprocess.check_call(popen_args, shell=False)  # noqa
    except subprocess.CalledProcessError as ex:
        inform(ex)
        sys.exit(ex.returncode)
    except Exception as ex:
        inform(f"Error: {ex} with script: {script} and args {args}")
        sys.exit(1)


def execute_with_environment(command: str, env: Dict[str, str]) -> Tuple[bytes, bytes]:
    """
    Yet another helper to execute a command
    """
    # Python 2 code! Python 3 uses context managers.
    command_text = command.strip().replace("  ", " ")
    command_parts = shlex.split(command_text)
    shell_process = subprocess.Popen(command_parts, env=env)
    value = shell_process.communicate()  # wait
    if shell_process.returncode != 0:
        inform(f"Didn't get a zero return code, got : {shell_process.returncode}")
        sys.exit(-1)
    return value
