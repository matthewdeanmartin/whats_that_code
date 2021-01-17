"""
Code checks, but tool is a node app.
"""
from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple
from navio_tasks.utils import inform


def do_pyright() -> str:
    """
    Execute pyright
    """

    command = "pyright"
    if check_command_exists(command, throw_on_missing=False):
        # subprocess.check_call(("npm install -g pyright").split(" "), shell=True)
        inform(
            "You must install pyright before doing pyright checks: "
            "npm install -g pyright"
        )
    command = prepinform_simple(command)
    command += "/**/*.py"
    execute(*(command.split(" ")))
    return "Pyright finished"
