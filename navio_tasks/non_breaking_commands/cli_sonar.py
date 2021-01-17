"""
Sonar complains about
- yaml formatting
- code complexity
- commented code
- (dead code?)
- duplicate code

Not all of those are equally actionable
"""

import json
import os
import sys

import requests

from navio_tasks.cli_commands import execute
from navio_tasks.output import say_and_exit
from navio_tasks.settings import PROJECT_NAME, VENV_SHELL
from navio_tasks.system_info import is_windows
from navio_tasks.utils import inform


def do_sonar() -> str:
    """
    Upload code to sonar for review
    """
    sonar_key = os.environ["SONAR_KEY"]
    if is_windows():
        command_name = "sonar-scanner.bat"
    else:
        command_name = "sonar-scanner"
    command = (
        f"{VENV_SHELL} {command_name} "
        f"-Dsonar.login={sonar_key} "
        "-Dproject.settings="
        "sonar-project.properties".strip().replace("  ", " ").split(" ")
    )
    inform(command)
    execute(*command)
    url = (
        "https://code-quality-test.loc.gov/api/issues/search?"
        f"componentKeys=public_record_{PROJECT_NAME}&resolved=false"
    )

    session = requests.Session()
    session.auth = (sonar_key, "")

    response = session.get(url)

    errors_file = "sonar.json"
    with open(errors_file, "w+") as file_handle:
        inform(response.text)
        text = response.text
        if not text:
            say_and_exit("Failed to check for sonar", "sonar")
            sys.exit(-1)
        file_handle.write(text)

    try:
        with open(errors_file) as file_handle:
            data = json.load(file_handle)

        if data["issues"]:
            for result in data["issues"]:
                inform(
                    "{} : {} line {}-{}".format(
                        result["component"],
                        result["message"],
                        result["textRange"]["startLine"],
                        result["textRange"]["endLine"],
                    )
                )
            say_and_exit("sonar has issues with this code", "sonar")
    except json.JSONDecodeError:
        pass
    return "Sonar done"
