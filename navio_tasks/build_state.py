"""
Make best efforts to decide if a task needs to run again, or if it is pointless
because the source code hasn't changed.

Sometimes task depends on the world, not the source code

Strategies
- folder or source tree changed
- file changed
- list of files changed

Is it worse is lint counting. Move to different module?
"""
import functools
import hashlib
import os
import shutil
import sys
import time
from typing import Any, Callable, Optional, TypeVar, cast

from checksumdir import dirhash

from navio_tasks import settings as settings
from navio_tasks.settings import PROJECT_NAME, SRC
from navio_tasks.utils import inform

# pylint: disable=invalid-name
FuncType = Callable[..., Any]
# pylint: disable=invalid-name
F = TypeVar("F", bound=FuncType)
CURRENT_HASH = None

# bash to find what has change recently
# find src/ -type f -print0 | xargs -0 stat -f "%m %N" | sort -rn | head -10 |
# cut -f2- -d" "


class BuildState:
    """
    Try not to re-do what doesn't need to be redone
    """

    def __init__(self, what: str, directory: str) -> None:
        """
        Set initial state
        """
        self.what = what
        self.directory = directory
        if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
            os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
        self.state_file_name = (
            f"{settings.CONFIG_FOLDER}/.build_state/last_change_{what}.txt"
        )

    def oh_never_mind(self) -> None:
        """
        If a task fails, we don't care if it didn't change since last, re-run,
        """
        # noinspection PyBroadException
        # pylint: disable=bare-except
        try:
            os.remove(self.state_file_name)
        except:  # noqa: B001
            pass

    def has_source_code_tree_changed(self) -> bool:
        """
        If a task succeeds & is re-run and didn't change, we might not
        want to re-run it if it depends *only* on source code
        """
        # pylint: disable=global-statement
        global CURRENT_HASH
        directory = self.directory

        # if CURRENT_HASH is None:
        # inform("hashing " + directory)
        # inform(os.listdir(directory))
        CURRENT_HASH = dirhash(
            directory,
            "md5",
            ignore_hidden=True,
            # changing these exclusions can cause dirhas to skip EVERYTHING
            # excluded_files=[".coverage", "lint.txt"],
            excluded_extensions=[".pyc"],
        )

        inform("Searching " + self.state_file_name)
        if os.path.isfile(self.state_file_name):
            with open(self.state_file_name, "r+") as file:
                last_hash = file.read()
                if last_hash != CURRENT_HASH:
                    file.seek(0)
                    file.write(CURRENT_HASH)
                    file.truncate()
                    return True
                return False

        # no previous file, by definition not the same.
        with open(self.state_file_name, "w") as file:
            file.write(CURRENT_HASH)
            return True


def oh_never_mind(what: str) -> None:
    """
    If task fails, remove file that says it was recently run.
    Needs to be like this because tasks can change code (and change the hash)
    """
    state = BuildState(what, PROJECT_NAME)
    state.oh_never_mind()


def has_source_code_tree_changed(
    task_name: str, expect_file: Optional[str] = None
) -> bool:
    """
    Hash source code tree to know if it has changed

    Also check if an expected output file exists or not.
    """
    if expect_file:
        if os.path.isdir(expect_file) and not os.listdir(expect_file):
            os.path.dirname(expect_file)
            # output folder empty
            return True
        if not os.path.isfile(expect_file):
            # output file gone
            return True
    state = BuildState(task_name, os.path.join(SRC, PROJECT_NAME))
    return state.has_source_code_tree_changed()


def skip_if_no_change(name: str, expect_files: Optional[str] = None) -> F:
    """
    Don't run decorated task if nothing in the source has changed.
    """

    # https://stackoverflow.com/questions/5929107/decorators-with-parameters
    def real_decorator(func: F) -> F:
        """Wrapper"""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrapper"""
            if not has_source_code_tree_changed(name, expect_files):
                inform("Nothing changed, won't re-" + name)
                return lambda x: None
            try:
                return func(*args, **kwargs)
            except:  # noqa: B001
                oh_never_mind(name)
                raise

        return cast(F, wrapper)

    return cast(F, real_decorator)


def hash_it(path: str) -> str:
    """
    Hash a single file. Return constant if it doesn't exist.
    """
    if not os.path.exists(path):
        return "DOESNOTEXIST"
    with open(path, "rb") as file_handle:
        return hashlib.sha256(file_handle.read()).hexdigest()


def skip_if_this_file_does_not_change(name: str, file: str) -> F:
    """
    Skip decorated task if this referenced file didn't change. Useful
    if a task depends on a single file and not (potentially) any file in the source tree
    """

    def real_decorator(func: F) -> F:
        """Wrapper"""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrapper"""
            state_file = (
                f"{settings.CONFIG_FOLDER}/.build_state/file_hash_" + name + ".txt"
            )
            previous_hash = "catdog"
            if os.path.exists(state_file):
                with open(state_file) as old_file:
                    previous_hash = old_file.read()

            new_hash = hash_it(file)
            if new_hash == previous_hash:
                inform("Nothing changed, won't re-" + name)
                return lambda x: f"Skipping {name}, no change"
            if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
                os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
            with open(state_file, "w+") as state:
                state.write(new_hash)
            try:

                return func(*args, **kwargs)
            except:  # noqa: B001
                # reset if step fails
                os.remove(state_file)
                raise

        return cast(F, wrapper)

    return cast(F, real_decorator)


def reset_build_state() -> None:
    """
    Delete all .build_state & to force all steps to re-run next build
    """
    if os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        shutil.rmtree(f"{settings.CONFIG_FOLDER}/.build_state")
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")


def timed() -> F:
    """This decorator prints the execution time for the decorated function."""

    def real_decorator(func: F) -> F:
        """Wrapper"""

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable:
            """Wrapper"""
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            inform("{} ran in {}s".format(func.__name__, round(end - start, 2)))
            return result

        return cast(F, wrapper)

    return cast(F, real_decorator)


def is_it_worse(task_name: str, current_rows: int, margin: int) -> bool:
    """
    Logic for dealing with a code base with very large amounts of lint.

    You will never fix it all, just don't make it worse.
    """
    if not os.path.exists(f"{settings.CONFIG_FOLDER}/.build_state"):
        os.makedirs(f"{settings.CONFIG_FOLDER}/.build_state")
    file_name = f"{settings.CONFIG_FOLDER}/.build_state/last_count_{task_name}.txt"

    last_rows = sys.maxsize
    if os.path.isfile(file_name):
        with open(file_name, "r+") as file:
            last_rows = int(file.read())
            if last_rows != current_rows:
                file.seek(0)
                file.write(str(current_rows))
                file.truncate()

    return current_rows > (last_rows + margin)
