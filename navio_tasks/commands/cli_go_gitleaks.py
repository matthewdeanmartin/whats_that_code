"""
Implemented in go.

Hangs on my workstation.
"""
import os
import shlex
import subprocess

from navio_tasks.settings import PROJECT_NAME
from navio_tasks.utils import inform


def run_gitleaks() -> None:
    """
    Run the gitleaks command.

    Depends on go!
    """
    #  git remote get-url --all origin
    # So far nothing works... as if current repo is corrupt
    cwd = os.getcwd()
    command_text = "gitleaks --repo-path={} --report=/tmp/{}.csv".format(
        cwd, PROJECT_NAME
    ).strip()
    inform(command_text)
    command = shlex.split(command_text)
    _ = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            "GOPATH": os.path.expandvars("$HOME/gocode"),
            "PATH": os.path.expandvars("$PATH/$GOPATH/bin"),
        },
        # shell=False, # keep false if possible.
        check=True,
    )
