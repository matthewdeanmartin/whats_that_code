"""
Settings loaded from pynt.ini

Maybe move to pyproject.toml?
"""
import configparser
import os
import platform

from navio_tasks.network import check_public_ip, is_known_network

CONFIG_FOLDER = ".config"


def load_config() -> configparser.SectionProxy:
    """
    Load config
    """
    config = configparser.ConfigParser()
    config.read(f"{CONFIG_FOLDER}/.pynt")
    return config["DEFAULT"]


SECTION = load_config()
PROJECT_NAME = SECTION["PROJECT_NAME"]

SRC = SECTION["SRC"]
PROBLEMS_FOLDER = SECTION["PROBLEMS_FOLDER"]
REPORTS_FOLDER = SECTION["REPORTS_FOLDER"]
IS_SHELL_SCRIPT_LIKE = SECTION["IS_SHELL_SCRIPT_LIKE"].lower() in ["true", "1"]
COMPLEXITY_CUT_OFF = SECTION["COMPLEXITY_CUT_OFF"]

MINIMUM_TEST_COVERAGE = int(SECTION["MINIMUM_TEST_COVERAGE"])
SMALL_CODE_BASE_CUTOFF = int(SECTION["SMALL_CODE_BASE_CUTOFF"])
MAXIMUM_LINT = int(SECTION["MAXIMUM_LINT"])
MAXIMUM_MYPY = int(SECTION["MAXIMUM_MYPY"])
MAXIMUM_DEAD_CODE = int(SECTION["MAXIMUM_DEAD_CODE"])
MAXIMUM_MANIFEST_ERRORS = int(SECTION["MAXIMUM_MANIFEST_ERRORS"])

VENV_SHELL = SECTION["VENV_SHELL"]


PACKAGE_WITH = SECTION["PACKAGE_WITH"]
if PACKAGE_WITH not in ["poetry", "setup.py", "None", "none"]:
    raise TypeError("PACKAGE_WITH must be poetry, setup.py or None")
if PACKAGE_WITH in ["None", "none"]:
    PACKAGE_WITH = ""

# pylint: disable=simplifiable-if-expression
# uh... need mechanism to show preference for no venv, poetry or pipenv.
# WANT_TO_USE_PIPENV = True if VENV_SHELL else False
PIPENV_ACTIVE = "PIPENV_ACTIVE" in os.environ and os.environ["PIPENV_ACTIVE"] == "1"
POETRY_ACTIVE = "POETRY_ACTIVE" in os.environ and os.environ["POETRY_ACTIVE"] == "1"
PIP_ACTIVE = "VIRTUAL_ENV" in os.environ and not PIPENV_ACTIVE and not POETRY_ACTIVE
TOX_ACTIVE = "TOX_PACKAGE" in os.environ
if PIPENV_ACTIVE:
    INSTALL_WITH = "pipenv"
elif POETRY_ACTIVE:
    INSTALL_WITH = "poetry"
elif PIP_ACTIVE or TOX_ACTIVE:
    INSTALL_WITH = "pip"
else:
    for key, value in os.environ.items():
        print(key, value)
    raise TypeError(
        "neither pipenv, poetry, nor pip virtual env active. "
        "Do we really want to use the system python?"
    )


if PIPENV_ACTIVE or POETRY_ACTIVE:
    # activating each run is very, very slow.
    VENV_SHELL = ""

PYTHON = "python"
IS_DJANGO = False
IS_GITLAB = "GITLAB_CI" in os.environ
IS_WINDOWS = platform.system() == "Windows"
IS_ALPINE_DOCKER = os.path.exists("/etc/alpine-release")
IS_JENKINS = "FROM_JENKINS" in os.environ and os.environ["FROM_JENKINS"] == "TRUE"

CURRENT_HASH = None

VENDOR_LIBS = ":"

# so that formatting doesn't run after check done once
FORMATTING_CHECK_DONE = False

# network call
PUBLIC_IP = check_public_ip()
KNOWN_IP_PREFIX = SECTION["KNOWN_IP_PREFIX"]
RUN_ALL_TESTS_REGARDLESS_TO_NETWORK = (
    SECTION["RUN_ALL_TESTS_REGARDLESS_TO_NETWORK"] == "True"
)
IS_INTERNAL_NETWORK = is_known_network(KNOWN_IP_PREFIX) or PUBLIC_IP.startswith(
    KNOWN_IP_PREFIX
)
IS_INTERACTIVE = not (IS_GITLAB or IS_JENKINS)

SPEAK_WHEN_BUILD_FAILS = SECTION["SPEAK_WHEN_BUILD_FAILS"] == "True"
