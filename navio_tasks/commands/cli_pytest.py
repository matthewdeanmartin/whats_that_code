"""
Only reports
No file changes
Should break build on any issues.
Expect few issues
All issues should be addressable immediately.
----------
"""
import multiprocessing

from navio_tasks.cli_commands import (
    check_command_exists,
    config_pythonpath,
    execute_with_environment,
)
from navio_tasks.settings import (
    IS_GITLAB,
    IS_INTERNAL_NETWORK,
    MINIMUM_TEST_COVERAGE,
    PROJECT_NAME,
    REPORTS_FOLDER,
    VENV_SHELL,
    RUN_ALL_TESTS_REGARDLESS_TO_NETWORK,
)
from navio_tasks.utils import inform


def do_pytest() -> None:
    """
    Pytest and coverage, which replaces nose tests
    """
    check_command_exists("pytest")

    #  Somedays VPN just isn't there.
    if IS_INTERNAL_NETWORK or RUN_ALL_TESTS_REGARDLESS_TO_NETWORK:
        fast_only = False
    else:
        fast_only = True
    if fast_only:
        test_folder = "test/test_fast"
        minimum_coverage = 48
    else:
        test_folder = "test"
        minimum_coverage = MINIMUM_TEST_COVERAGE

    my_env = config_pythonpath()

    command = (
        f"{VENV_SHELL} pytest {test_folder} -v "
        f"--junitxml={REPORTS_FOLDER}/sonar-unit-test-results.xml "
        "--cov-report xml "
        f"--cov={PROJECT_NAME} "
        f"--cov-fail-under {minimum_coverage}".strip().replace("  ", " ")
        + " --quiet"  # 15000 pages of call stack don't help anyone
    )
    # when it works, it is FAST. when it doesn't, we get lots of timeouts.
    # if not IS_GITLAB:
    #     command += f" -n {multiprocessing.cpu_count()} "
    if not IS_GITLAB:
        command += " -n 2 "

    inform(command)
    execute_with_environment(command, my_env)
    inform("Tests will not be re-run until code changes. Run pynt reset to force.")


def do_pytest_coverage(fast_only: bool) -> None:
    """
    Just the coverage report
    """
    # this is failing on windows
    # check_command_exists("py.test")

    my_env = config_pythonpath()

    # generate report separate from cov-fail-under step.
    # py.test incorrectly reports 0.00 coverage,
    # but only when reports are generated.

    # Coverage report is (sometimes) broken. Need alternative to py.test?
    # This is consuming too much time to figure out why it
    # collects no tests & then fails on code 5

    if fast_only:
        test_folder = "test/test_fast"
    else:
        test_folder = "test"

    command = (
        f"{VENV_SHELL} pytest {test_folder} -v "
        "--cov-report html:coverage "
        f"--cov={PROJECT_NAME}".strip().replace("  ", " ")
    )
    if not IS_GITLAB:
        command += f" -n {multiprocessing.cpu_count()} "
    inform(command)
    execute_with_environment(command, my_env)
    inform("Coverage will not rerun until code changes. Run `pynt reset` to force")
