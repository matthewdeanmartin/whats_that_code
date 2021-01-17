"""
Build tasks

This file should be concerned with the work flow and some business rules
about what tasks to run. The parameters to those business rules should be handed
off to the relevant tool in the /commands/ folder

- don't run cli commands directly here, put that in a separate file
- this is a good place for deciding if *this* project needs to run a command
- the commands may have code to handle if it makes sense to run a command, e.g.
  don't run git commands if not in a repo

Applying to new projects, for each tool (assuming all tools are value add)

- does this apply at all?
- should it stop the build if it fails? eg. unit tests, mypy, lint should fail the build
- is it a periodic report?

Decisions will vary based on:
- is the tool fast (do fast tools first so they can fail fast)
- does it change files (upgrade, reformat)
    - These can't run in parallel, should run before quality checks
    - Doesn't make sense on build server (no one there to check in changes)
- does it depend only on source (needs only re-run on source changes, not true of
  integration tests)
- is it immediately actionable?
    - Code size reports- Removing a sixth argument might make the code worse
    - Code complexity reports - not safe to simplify the most complex code every day!

"""

import functools
import os
import subprocess
import sys

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    if "PIPENV_ACTIVE" in os.environ:
        print("I can see we are in a pipenv environment, but dependencies are missing.")
    if "POETRY_ACTIVE" in os.environ:
        print("I can see we are in a poetry environment, but dependencies are missing.")
    if "VIRTUAL_ENV" in os.environ:
        print(
            "I can see we are in a virtual environment,"
            " but dependencies are missing."
        )

    print(
        "dotenv not found... most likely you need to create a virtual env\n"
        "and install all the build dependencies, or activate it"
    )
    print("\n see pipx_install.sh for things like black and pylint.")
    print("\n Pipenv install --dev or the equivallent for everything else")

    exit(-1)
from navio_tasks.commands.cli_go_gitleaks import run_gitleaks
from navio_tasks.dependency_commands.cli_installs import do_dependency_installs
from navio_tasks.mutating_commands.cli_precommit import do_precommit
from navio_tasks.commands.cli_npm_pyright import do_pyright
from pebble import ProcessPool

from navio.builder import task

# on some shells print doesn't flush!
# pylint: disable=redefined-builtin,invalid-name
from navio_tasks.build_state import (
    timed,
    skip_if_no_change,
    skip_if_this_file_does_not_change,
    reset_build_state,
)
from navio_tasks.clean import clean_old_files
from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.commands.cli_bandit import do_bandit
from navio_tasks.commands.cli_compile_py import do_compile_py
from navio_tasks.commands.cli_detect_secrets import do_detect_secrets
from navio_tasks.commands.cli_flake8 import do_flake8
from navio_tasks.commands.cli_get_secrets import do_git_secrets
from navio_tasks.commands.cli_mypy import do_mypy, evaluated_mypy_results
from navio_tasks.commands.cli_pylint import do_lint, evaluated_lint_results
from navio_tasks.commands.cli_pyt import do_python_taint
from navio_tasks.commands.cli_pytest import do_pytest, do_pytest_coverage
from navio_tasks.commands.cli_tox import do_tox
from navio_tasks.commands.lib_dodgy import do_dodgy
from navio_tasks.dependency_commands.cli_liccheck import do_liccheck
from navio_tasks.dependency_commands.cli_pin_dependencies import (
    convert_pipenv_to_requirements,
)
from navio_tasks.dependency_commands.cli_pip import do_pip_check, do_register_scripts
from navio_tasks.dependency_commands.cli_safety import do_safety
from navio_tasks.deprecated_commands.cli_check_manifest import do_check_manifest
from navio_tasks.deprecated_commands.cli_pyroma import do_pyroma
from navio_tasks.deprecated_commands.cli_setup_py import (
    do_package,
    do_project_validation_for_setup_py,
)
from navio_tasks.file_system import initialize_folders
from navio_tasks.mutating_commands.cli_black import do_formatting
from navio_tasks.mutating_commands.cli_isort import do_isort
from navio_tasks.mutating_commands.cli_jiggle_version import do_jiggle_version
from navio_tasks.mutating_commands.cli_pyupgrade import do_pyupgrade
from navio_tasks.non_breaking_commands.cli_mccabe import do_mccabe
from navio_tasks.non_breaking_commands.cli_scspell import do_spell_check
from navio_tasks.non_breaking_commands.cli_sonar import do_sonar
from navio_tasks.non_breaking_commands.cli_vulture import do_vulture
from navio_tasks.non_py_commands.cli_openapi import do_openapi_check
from navio_tasks.non_py_commands.cli_yamllint import do_yamllint
from navio_tasks.packaging_commands.cli_twine import do_upload_package
from navio_tasks.pure_reports.cli_gitchangelog import do_gitchangelog
from navio_tasks.pure_reports.cli_pygount import do_count_lines_of_code
from navio_tasks.pure_reports.cli_sphinx import do_docs
from navio_tasks.settings import (
    PROJECT_NAME,
    POETRY_ACTIVE,
    PIPENV_ACTIVE,
    VENV_SHELL,
    PROBLEMS_FOLDER,
    IS_GITLAB,
    PYTHON,
    IS_INTERNAL_NETWORK,
    SMALL_CODE_BASE_CUTOFF,
    MAXIMUM_LINT,
    MAXIMUM_MYPY,
    IS_INTERACTIVE,
    PACKAGE_WITH,
    IS_SHELL_SCRIPT_LIKE,
    RUN_ALL_TESTS_REGARDLESS_TO_NETWORK,
)

print = functools.partial(print, flush=True)  # noqa

if os.path.exists(".env"):
    load_dotenv()

initialize_folders()

# If node exists, we can run node build tools.
NODE_EXISTS = check_command_exists(
    "node", throw_on_missing=False, exit_on_missing=False
)

clean_old_files()


@task()
@timed()
def check_python_version() -> None:
    """
    Possibly should look up min value in Pipenv or .pynt
    """
    print(sys.version_info)
    if sys.version_info[0] < 3:
        print("Must be using Python 3.7")
        sys.exit(-1)
    if sys.version_info[1] < 7:
        print("Must be using Python 3.7 or greater")
        sys.exit(-1)


@task(check_python_version)
@skip_if_no_change("compile_py")
@timed()
def compile_py() -> None:
    """
    Basic syntax check with compileall flag
    """
    # policy decision, which python version to use.
    do_compile_py(PYTHON)


@task()
@timed()
def validate_project_name() -> None:
    """
    Verify that all projects/modules are explicitly declared
    """
    do_project_validation_for_setup_py()


@task()
@timed()
@skip_if_this_file_does_not_change("installs", file="Pipfile")
def pipenv_installs() -> None:
    """
    Catch up on installs
    """
    # , but only when Pipfile changes because pipenv is so slow
    do_dependency_installs(PIPENV_ACTIVE, POETRY_ACTIVE, PIPENV_ACTIVE)


@task()
@timed()
def gitchangelog() -> None:
    """
    Create a change log from git comments
    """
    do_gitchangelog()


@task()
@skip_if_no_change("git_leaks")
@timed()
def git_leaks() -> None:
    """
    Depends on go!
    """
    run_gitleaks()


@task()
@skip_if_no_change("git_secrets")
@timed()
def git_secrets() -> None:
    """
    Run git secrets utility
    """
    do_git_secrets()


@task()
@timed()
def reset() -> None:
    """
    Delete all .build_state & to force all steps to re-run next build
    """
    reset_build_state()


@task(pipenv_installs)
@skip_if_no_change("pyupgrade")
@timed()
def pyupgrade() -> str:
    """
    Pyupgrade
    """
    # supported py3, py36, py37, py38
    # Should be logically consistent with other minimum python version
    # tools (vermin, compile_py, tox)
    return do_pyupgrade(IS_INTERACTIVE, "py38")


@task()
@timed()
def isort() -> None:
    """Sort the imports to discover import order bugs and prevent import order bugs"""
    # This must run before black. black doesn't change import order but it wins
    # any arguments about formatting.
    # isort MUST be installed with pipx! It is not compatible with pylint in the same
    # venv. Maybe someday, but it just isn't worth the effort.
    do_isort()


@task(pipenv_installs, pyupgrade, compile_py, isort)
@skip_if_no_change("formatting")
@timed()
def formatting() -> None:
    """
    Format main project with black
    """
    do_formatting("", BLACK_STATE)


@task()
@skip_if_no_change("format_tests")
@timed()
def format_tests() -> None:
    """
    Format unit tests with black
    """
    do_formatting("test", {"check_already_done": False})


BLACK_STATE = {"check_already_done": False}


@task(pipenv_installs, compile_py)
@timed()
def formatting_check() -> None:
    """
    Call with check parameter
    """
    do_formatting("--check", BLACK_STATE)


@task()
@timed()
@skip_if_this_file_does_not_change("pyroma", "setup.py")
def pyroma() -> None:
    """
    Pyroma linter
    """
    # technically, this can depend on setup.py or setup.cfg...
    do_pyroma()


@task()
@skip_if_this_file_does_not_change("docker_lint", "Dockerfile")
@timed()
def docker_lint() -> None:
    """
    Lint the dockerfile
    """
    with open("Dockerfile") as my_input, open(
        f"{PROBLEMS_FOLDER}/docker_lint.txt", "w"
    ) as my_output:
        # ignore = ""  # "--ignore DL3003 --ignore DL3006"
        command = "docker run --rm -i hadolint/hadolint hadolint -".strip()
        _ = subprocess.run(command, stdin=my_input, stdout=my_output, check=True)


@task()
@timed()
def spell_check() -> None:
    """
    Check spelling using scspell (pip install scspell3k)
    """
    do_spell_check()


@task()
@skip_if_no_change("yamllint")
@timed()
def yaml_lint() -> str:
    """
    Check yaml files for problems
    """
    return do_yamllint()


@task()
@skip_if_no_change("count_lines_of_code")
@timed()
def count_lines_of_code() -> None:
    """
    Count lines of code to set build strictness
    """
    do_count_lines_of_code()


@task(formatting, compile_py)
@skip_if_this_file_does_not_change("liccheck", "Pipfile")
@timed()
def liccheck() -> None:
    """
    Force an explicit decision about license of referenced packages
    """
    do_liccheck()


@task(formatting, compile_py)
@skip_if_no_change("pyright")
@timed()
def pyright() -> None:
    """
    Pyright checks. NODEJS TOOOL!
    """
    do_pyright()


@task(formatting, compile_py)
@skip_if_no_change("flake8")
@timed()
def flake8() -> None:
    """
    Lint with flake8
    """
    do_flake8()


@task(formatting, compile_py)
@skip_if_no_change("bandit")
@timed()
def bandit() -> None:
    """
    Security linting with bandit
    """
    # bandit thinks any use of subprocess is inherently insecure.
    # These two exist for running shell commands.
    # /scripts/ folder
    # build.py itself
    do_bandit(IS_SHELL_SCRIPT_LIKE)


@task(formatting, compile_py)
@skip_if_no_change("python_taint")
@timed()
def python_taint() -> None:
    """
    Security linting with pyt
    """
    do_python_taint()


@task(flake8)
@skip_if_no_change("mccabe")
@timed()
def mccabe() -> None:
    """
    Complexity checking/reports with mccabe
    """
    do_mccabe()


@task(formatting, compile_py)
@skip_if_no_change("dodgy")
@timed()
def dodgy_check() -> None:
    """
    Linting with dodgy
    """
    do_dodgy()


@task()
@skip_if_no_change("detect_secrets")
@timed()
def detect_secrets() -> None:
    """
    Look for secrets using detect-secrets
    """
    # pylint: disable=unreachable
    do_detect_secrets()


@task(formatting_check)
@skip_if_no_change("precommit")
@timed()
def precommit() -> None:
    """
    Build time execution of pre-commit checks. Modifies code so run before linter.
    """
    do_precommit(IS_INTERACTIVE)


@task()
@timed()
def openapi_check():
    """Run several tools on the api yaml"""
    do_openapi_check()


@task(compile_py, formatting, count_lines_of_code, openapi_check)
@skip_if_no_change("lint", expect_files=f"{PROBLEMS_FOLDER}/lint.txt")
@timed()
def lint() -> None:
    """
    Lint with pylint
    """
    lint_file = do_lint(PROJECT_NAME)

    fatals = ["no-member", "no-name-in-module", "import-error"]
    evaluated_lint_results(
        lint_output_file_name=lint_file,
        small_code_base_cut_off=SMALL_CODE_BASE_CUTOFF,
        maximum_lint=MAXIMUM_LINT,
        fatals=fatals,
    )


@task(format_tests)
@skip_if_no_change("lint_tests", expect_files=f"{PROBLEMS_FOLDER}/lint_test.txt")
@timed()
def lint_tests() -> None:
    """
    Lint only the tests by a different rule set
    """
    lint_file = do_lint("test")

    evaluated_lint_results(
        lint_output_file_name=lint_file,
        small_code_base_cut_off=SMALL_CODE_BASE_CUTOFF,
        maximum_lint=MAXIMUM_LINT,
        fatals=[],
    )


@task()
@timed()
def tox() -> None:
    """Check fast tests on current + next python"""
    do_tox()


@task()
@skip_if_no_change("pytest", expect_files=f"{PROBLEMS_FOLDER}/pytest.txt")
@timed()
def pytest() -> None:
    do_pytest()


@task()
@skip_if_no_change(
    "coverage_report", expect_files=f"{PROBLEMS_FOLDER}/coverage_report.txt"
)
@timed()
def coverage_report() -> None:
    """
    Just the coverage report
    """
    # Integration vs non integration
    # slow vs fast
    # on network vs not on network
    if IS_INTERNAL_NETWORK or RUN_ALL_TESTS_REGARDLESS_TO_NETWORK:
        fast_only = False
    else:
        fast_only = True
    do_pytest_coverage(fast_only=fast_only)


@task()
@skip_if_no_change("docs")
@timed()
def docs() -> None:
    """
    Generate Sphynx documentation
    """
    do_docs()


@task()
@skip_if_this_file_does_not_change("openapi_check", f"{PROJECT_NAME}/api.yaml")
@timed()
def openapi_check() -> None:
    """
    Does swagger/openapi file parse
    """
    do_openapi_check()


@task()
@timed()
@skip_if_this_file_does_not_change("pip_check", "Pipfile")
def pip_check() -> None:
    """
    pip check the packages
    """
    do_pip_check()


@task()
@timed()
@skip_if_this_file_does_not_change("safety", "Pipfile")
def safety() -> None:
    """
    Run safety against pinned requirements
    """
    do_safety()


@task()  # this depends on coverage! blows up if xml file doesn't match source
@skip_if_no_change("sonar", expect_files="sonar.json")
@timed()
def sonar() -> None:
    """
    Lint using remote sonar service
    """
    do_sonar()


@task(count_lines_of_code)
@skip_if_no_change("mypy", expect_files=f"{PROBLEMS_FOLDER}/mypy_errors.txt")
@timed()
def mypy() -> None:
    """
    Check types using mypy
    """
    skips = [
        "tests.py",
        "/test_",
        "/tests_",
        # No clear way to type a decorator
        "Untyped decorator",
        "<nothing> not callable",
        'Returning Any from function declared to return "Callable[..., Any]"',
        'Missing type parameters for generic type "Callable"',
        # certain modules
        "pymarc",
    ]
    result = do_mypy()
    evaluated_mypy_results(result, SMALL_CODE_BASE_CUTOFF, MAXIMUM_MYPY, skips)


@task()
@timed()
@skip_if_this_file_does_not_change("pin_dependencies", "Pipfile")
def pin_dependencies() -> None:
    """
    Create requirement*.txt
    """
    convert_pipenv_to_requirements(pipenv=True)


@task()
@skip_if_no_change("vulture", expect_files=f"{PROBLEMS_FOLDER}/dead_code.txt")
@timed()
def vulture() -> None:
    """
    Find dead code using vulture
    """
    do_vulture()


@task(count_lines_of_code)
@skip_if_no_change("check_manifest", f"{PROBLEMS_FOLDER}/manifest_errors.txt")
@timed()
def check_manifest() -> None:
    """
    Find files missing from MANIFEST.in
    """
    if PACKAGE_WITH == "setup.py":
        do_check_manifest()


@task()
@timed()
def jiggle_version() -> None:
    """
    Increase build number of version, but only if this is the master branch.
    """
    do_jiggle_version(is_interactive=IS_INTERACTIVE)


@task(
    formatting,  # changes source
    # TODO: switch to parallel
    mypy,
    detect_secrets,
    git_secrets,
    vulture,
    compile_py,
    lint,
    flake8,
    dodgy_check,
    bandit,
    python_taint,
    mccabe,
    pin_dependencies,
    jiggle_version,
    check_manifest,
    # tests as slow as tests are.
    pytest,
    # nose
    # package related
    liccheck,
    pyroma,
    pip_check,
    safety,
    precommit,  # I hope this doesn't change source anymore
)  # docs ... later
@skip_if_no_change("package")
@timed()
def package() -> None:
    """
    package, but don't upload
    """
    do_package()


@task()
@timed()
@skip_if_no_change("parallel_checks")
def parallel_checks() -> None:
    """
    Do all the checks that don't change code and can run in parallel.
    """
    chores = [
        do_mypy,
        do_detect_secrets,
        do_git_secrets,
        vulture,
        do_compile_py,
        do_lint,
        do_flake8,
        do_dodgy,
        do_bandit,
        do_python_taint,
        do_mccabe,
        do_check_manifest,
        do_liccheck,
    ]
    if IS_GITLAB:
        # other tasks assume there will be a LOC file by now.
        do_count_lines_of_code()
        for chore in chores:
            print(chore())
        return

    # can't do pyroma because that needs a package, which might not exist yet.

    pool = ProcessPool(12)  # max_workers=len(chores))  # cpu_count())
    # log_to_stderr(logging.DEBUG)
    tasks = []
    for chore in chores:
        tasks.append(pool.schedule(chore, args=()))

    print("close & join")
    pool.close()
    pool.join()

    for current_task in tasks:
        # pylint: disable=broad-except
        try:
            result = current_task.result()
            exception = current_task.exception()
            if exception:
                print(current_task.exception())
            print(result)
            if "Abnormal" in str(result):
                print("One or more parallel tasks failed.")
                sys.exit(-1)
        except Exception as ex:
            print(ex)
            sys.exit(-1)


@task(
    mypy,  #
    detect_secrets,
    git_secrets,
    vulture,
    compile_py,
    lint,
    flake8,
    dodgy_check,
    bandit,
    python_taint,
    mccabe,
    check_manifest,
    liccheck,  #
)  # docs ... later
@timed()
def slow() -> None:
    """
    Same tasks as parallel checks but in serial. For perf comparisons
    """


@task(
    formatting_check,  # changes source
    parallel_checks,
    # package related checks
    # pyroma, # depends on dist folder existing!
    # pip_check, # depends on dist folder existing!
    jiggle_version,  # changes source
    precommit,  # changes source
)  # docs ... later
@timed()
def fast_package() -> None:
    """
    Run most tasks in parallel
    """
    do_package()


@task()
@timed()
def just_package() -> None:
    """Package, but do no checks or tests at all"""
    print("WARNING: This skips all quality checks.")
    do_package()


@task()
@timed()
def check_package() -> None:
    """
    Run twine check
    """
    check_command_exists("twine")
    execute(*(f"{VENV_SHELL} twine check dist/*".strip().split(" ")))


@task()
@timed()
def upload_package() -> None:
    """
    Send to private package repo
    """
    do_upload_package()


# Conflicting dependencies and blows up on simple scan.
# def run_truffle_hog() -> None:
#     """
#     Run truffle hog command
#     """
#     # need to get the URL from 'git remote show origin'
#     command = (
#         "trufflehog --entropy False "
#         "ssh://git@git.loc.gov:7999/COP/public-records/search_ui.git"
#     )
#     print(command)


# FAST. FATAL ERRORS. DON'T CHANGE THINGS THAT CHECK IN
@task(mypy, detect_secrets, git_secrets, check_package, compile_py, vulture)
@skip_if_no_change("pre_commit_hook")
@timed()
def pre_commit_hook() -> None:
    """
    Everything that could be run as a pre_commit_hook

    Mostly superceded by precheck utility
    """
    # Don't format or update version
    # Don't do slow stuff- discourages frequent check in
    # Run checks that are likely to have FATAL errors, not just sloppy coding.


# Don't break the build, but don't change source tree either.
@task(mypy, detect_secrets, git_secrets, pytest, check_package, compile_py, vulture)
@skip_if_no_change("pre_push_hook")
@timed()
def pre_push_hook() -> None:
    """
    More stringent checks to run pre-push
    """
    # Don't format or update version
    # Don't do slow stuff- discourages frequent check in
    # Run checks that are likely to have FATAL errors, not just sloppy coding.


@task()
@skip_if_no_change("config_scripts")
@timed()
def register_scripts() -> None:
    do_register_scripts()


@task(gitchangelog)
@timed()
def reports() -> None:
    """
    Some build tasks can only be read by a human and can't automatically fail a build.
    For example, git activity reports, complexity metric reports and so on.

    TODO:
    Git reformatting - Authors/Contributors, Changelog
    complexity reports - Cure to complexity sometimes worse that the complexity
    coverage,- Human HTML report runs separately from coverage as quality gate
    dupe code & dead code - Unreliable at detecting real problems
    "grades"
    spelling - involves lengthy step of updating dictionary with false positives
    tox - slow test to say if we can safely upgrade to next version of python/dep
    upgrade report - query pypi for new versions
    source reformating - Sphinx docs
    """


# Default task (if specified) is run when no task is specified in the command line
# make sure you define the variable __DEFAULT__ after the task is defined
# A good convention is to define it at the end of the module
# __DEFAULT__ is an optional member

# __DEFAULT__ = echo
