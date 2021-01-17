"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
"""
import json
import shlex
import sys

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute_get_text,
)
from navio_tasks.output import say_and_exit
from navio_tasks.settings import PROBLEMS_FOLDER, VENV_SHELL
from navio_tasks.utils import inform


def do_detect_secrets() -> str:
    """
    Call detect-secrets tool

    I think this is the problem:

    # Code expects to stream output to file and then expects
    # interactive person, so code hangs. But also hangs in git-bash
    detect-secrets scan test_data/config.env > foo.txt
    detect-secrets audit foo.txt
    """
    inform("Detect secrets broken ... can't figure out why")
    return "nope"

    # pylint: disable=unreachable
    check_command_exists("detect-secrets")
    errors_file = f"{PROBLEMS_FOLDER}/detect-secrets-results.txt"
    command_text = (
        f"{VENV_SHELL} detect-secrets scan "
        "--base64-limit 4 "
        # f"--exclude-files .idea|.min.js|.html|.xsd|"
        # f"lock.json|.scss|Pipfile.lock|.secrets.baseline|"
        # f"{PROBLEMS_FOLDER}/lint.txt|{errors_file}".strip().replace("  ", " ")
    )
    inform(command_text)
    command = shlex.split(command_text)

    with open(errors_file, "w") as outfile:
        env = config_pythonpath()
        output = execute_get_text(command, ignore_error=False, env=env)
        outfile.write(output)
        # subprocess.call(command, stdout=outfile, env=env)

    with open(errors_file, "w+") as file_handle:
        text = file_handle.read()
        if not text:
            say_and_exit("Failed to check for secrets", "detect-secrets")
            sys.exit(-1)
        file_handle.write(text)

    try:
        with open(errors_file) as json_file:
            data = json.load(json_file)

        if data["results"]:
            for result in data["results"]:
                inform(result)
            say_and_exit(
                "detect-secrets has discovered high entropy strings, "
                "possibly passwords?",
                "detect-secrets",
            )
    except json.JSONDecodeError:
        pass
    return "Detect secrets completed."
