"""
Reorg imports. Constant 4 way battle between black, isort, pycharm and mscode
"""
from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple


def do_isort() -> str:
    """Sort the imports to discover import order bugs and prevent import order bugs"""
    # This must run before black. black doesn't change import order but it wins
    # any arguments about formatting.
    # isort MUST be installed with pipx! It is not compatible with pylint in the same
    # venv. Maybe someday, but it just isn't worth the effort.

    check_command_exists("isort")
    command = "isort --profile black"
    command = prepinform_simple(command)
    execute(*(command.split(" ")))
    return "isort succeeded"
