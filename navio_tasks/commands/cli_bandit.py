"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
"""


from navio_tasks.cli_commands import check_command_exists, execute, prepinform_simple


def do_bandit(is_shell_script_like: bool) -> str:
    """
    Security Checks

    Generally returns a small number of problems to fix.
    """
    if is_shell_script_like:
        return (
            "Skipping bandit, this code is shell script-like so it has security"
            "issues on purpose."
        )

    command = "bandit"
    check_command_exists(command)
    command = "bandit -r"
    command = prepinform_simple(command)
    execute(*(command.split(" ")))
    return "bandit succeeded"
