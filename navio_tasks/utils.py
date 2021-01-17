"""
Code from pynt until I can phase it out.
"""
import contextlib
import functools
import os
import sys
from subprocess import CalledProcessError, check_call
from typing import Any, Iterable


__license__ = "MIT License"
__contact__ = "http://rags.github.com/pynt-contrib/"

# pylint: disable=redefined-builtin
inform = functools.partial(print, flush=True)  # no qa


@contextlib.contextmanager
def safe_cd(path: str) -> Any:
    """
    Changes to a directory, yields, and changes back.
    Additionally any error will also change the directory back.

    Usage:
    # >>> with safe_cd('some/repo'):
    # ...     execute('git status')
    """
    starting_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(starting_directory)


def execute(script: str, *args: Iterable[str]) -> int:
    """
    Executes a command through the shell. Spaces should breakup the args.
    Usage: execute('grep', 'TODO', '*')
    """

    popen_args = [script] + list(args)
    # pylint: disable=broad-except
    try:
        return check_call(popen_args, shell=False)  # noqa
    except CalledProcessError as ex:
        inform(ex)
        sys.exit(ex.returncode)
    except Exception as ex:
        inform(f"Error: {ex} with script: {script} and args {args}")
        sys.exit(1)


#
# def inform(*args: Any) -> None:
#     print(args)

# keep this one
