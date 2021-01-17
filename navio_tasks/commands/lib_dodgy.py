"""
Security tool, rarely finds problems, cna't be called from commandline
"""
import os
import sys

from dodgy import run as dodgy_runner

from navio_tasks.output import say_and_exit
from navio_tasks.utils import inform


def do_dodgy() -> str:
    """
    Checks for AWS keys, diffs, pem keys
    """
    # Not using the shell command version because it mysteriously failed
    # and this seems to work fine.
    warnings = dodgy_runner.run_checks(os.getcwd())
    if warnings:

        for message in warnings:
            inform(message)
        say_and_exit("Dodgy found problems", "dodgy")
        sys.exit(-1)
    return "dodgy succeeded"
