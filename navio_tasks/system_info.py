"""
Infering what machine we are on.
"""
import os
import platform
import re
import socket
import git
import psutil

from navio_tasks.utils import inform


def is_git_repo(path: str) -> bool:
    """
    Are we in a git repo if not, several tools don't make sense to run
    https://stackoverflow.com/a/39956572/33264
    """
    try:
        _ = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


def is_windows() -> bool:
    """Guess if windows"""
    platform_string = platform.system()
    return os.name == "nt" or platform_string == "Windows" or "_NT" in platform_string


def is_powershell() -> bool:
    """
    Check if parent process or other ancestor process is powershell
    """
    # ref https://stackoverflow.com/a/55598796/33264
    # Get the parent process name.

    try:
        process_name = psutil.Process(os.getppid()).name()
        grand_process_name = psutil.Process(os.getppid()).parent().name()
        # See if it is Windows PowerShell (powershell.exe) or PowerShell Core
        # (pwsh[.exe]):
        is_that_shell = bool(re.fullmatch("pwsh|pwsh.exe|powershell.exe", process_name))
        if not is_that_shell:
            is_that_shell = bool(
                re.fullmatch("pwsh|pwsh.exe|powershell.exe", grand_process_name)
            )
    except psutil.NoSuchProcess:
        inform("Can't tell if this is powershell, assuming not.")
        is_that_shell = False
    return is_that_shell


def check_is_aws() -> bool:
    """
    Look at domain name to see if this is an ec2 machine
    """
    # HACK: environment variable checking is much, much faster & reliable.
    name = socket.getfqdn()
    return "ip-" in name and ".ec2.internal" in name
