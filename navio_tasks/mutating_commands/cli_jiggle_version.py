"""
Increase version number, but only the last number in a semantic version triplet
"""
import shlex

from git import InvalidGitRepositoryError, Repo

from navio_tasks.cli_commands import check_command_exists, execute
from navio_tasks.settings import PROJECT_NAME
from navio_tasks.utils import inform


def do_jiggle_version(
    is_interactive: bool,
    target_branch: str = "",
    increase_version_on_all_branches: bool = False,
) -> str:
    """
    Increase version number, but only the last number in a semantic version triplet
    """
    if not is_interactive:
        inform(
            "Not an interactive session, skipping jiggle_version, which changes files."
        )
        return "Skipping"
    # rorepo is a Repo instance pointing to the git-python repository.
    # For all you know, the first argument to Repo is a path to the repository
    # you want to work with
    try:
        repo = Repo(".")
        active_branch = str(repo.active_branch)
    except InvalidGitRepositoryError:
        inform("Can't detect what branch we are on. Is this a git repo?")
        active_branch = "don't know what branch we are on"

    if active_branch == target_branch or increase_version_on_all_branches:
        check_command_exists("jiggle_version")
        command = f"jiggle_version here --module={PROJECT_NAME}"
        parts = shlex.split(command)
        execute(*parts)
    else:
        inform("Not master branch, not incrementing version")
    return "ok"
