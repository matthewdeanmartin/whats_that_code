"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
"""
import subprocess

from navio_tasks import settings as settings
from navio_tasks.cli_commands import check_command_exists, execute


def do_safety() -> str:
    """
    Check free database for vulnerabilities in pinned libraries.
    """
    requirements_file_name = f"{settings.CONFIG_FOLDER}/requirements_for_safety.txt"
    with open(requirements_file_name, "w+") as out:
        subprocess.run(["pip", "freeze"], stdout=out, stderr=out, check=True)
    check_command_exists("safety")
    # ignore 38414 until aws fixes awscli
    execute("safety", "check", "--ignore", "38414", "--file", requirements_file_name)
    return "Package safety checked"
