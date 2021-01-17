"""
See if python compiles.

TODO: Maybe implement vermin, another compilation checker.
"""

import shlex

from navio_tasks.cli_commands import (
    config_pythonpath,
    execute_get_text,
    prepinform_simple,
)
from navio_tasks.utils import inform


def do_compile_py(python: str) -> str:
    """
    Catch only the worst syntax errors in the currently python version
    """
    command_text = f"{python} -m compileall"
    command_text = prepinform_simple(command_text)
    command = shlex.split(command_text)
    result = execute_get_text(command, env=config_pythonpath())
    for line in result.split("\n"):
        if line and (line.startswith("Compiling") or line.startswith("Listing")):
            pass
        else:
            inform(line)
    return "compileall succeeded"


# Vermin sample output
# Tip: You're using potentially backported modules: argparse, configparser, typing
# If so, try using the following for better results: --backport argparse
# --backport configparser --backport typing
#
# Minimum required versions: 3.6
# Incompatible versions:     2
