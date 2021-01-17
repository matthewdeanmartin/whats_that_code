"""
Removing old crap.

Trivial except when something has a lock on a file.
"""
import os


def clean_old_files() -> None:
    """
    Output files all moved to /problems/ or /reports/, clean up
    detritus left by old versions of build.py
    """
    for file in [
        "dead_code.txt",
        "lint.txt",
        "mypy_errors.txt",
        "line_counts.txt",
        "manifest_errors.txt",
        "detect-secrets-results.txt",
    ]:
        if os.path.exists(file):
            os.remove(file)
