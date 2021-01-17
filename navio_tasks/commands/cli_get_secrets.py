"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
-------
"""
import shlex
import subprocess

from navio_tasks.cli_commands import check_command_exists, execute, is_cmd_exe
from navio_tasks.settings import IS_GITLAB
from navio_tasks.system_info import check_is_aws, is_git_repo
from navio_tasks.utils import inform


def do_git_secrets() -> str:
    """
    Install git secrets if possible.
    """
    if is_cmd_exe():
        inform("git secrets is a bash script, only works in bash (or maybe PS")
        return "skipped git secrets, this is cmd.exe shell"
    # not sure how to check for a git subcommand
    if not is_git_repo("."):
        inform("This is not a git repo, won't run git-secrets")
        return "Not a git repo, skipped"
    check_command_exists("git")

    if check_is_aws():
        # no easy way to install git secrets on ubuntu.
        return "This is AWS, not doing git-secrets"
    if IS_GITLAB:
        inform("Nothing is edited on gitlab build server")
        return "This is gitlab, not doing git-secrets"
    try:
        # check to see if secrets even is a git command

        commands = ["git secrets --install", "git secrets --register-aws"]
        for command in commands:
            command_parts = shlex.split(command)
            command_process = subprocess.run(
                command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            for stream in [command_process.stdout, command_process.stderr]:
                if stream:
                    for line in stream.decode().split("\n"):
                        inform("*" + line)
    except subprocess.CalledProcessError as cpe:
        inform(cpe)
        installed = False
        for stream in [cpe.stdout, cpe.stderr]:
            if stream:
                for line in stream.decode().split("\n"):
                    inform("-" + line)
                    if "commit-msg already exists" in line:
                        inform("git secrets installed.")
                        installed = True
                        break
        if not installed:
            raise
    command_text = "git secrets --scan -r ./".strip().replace("  ", " ")
    command_parts = shlex.split(command_text)
    execute(*command_parts)
    return "git-secrets succeeded"
