"""
Classify 'em
"""

import os

from whats_that_code.election import guess_language_all_methods
from whats_that_code.known_languages import FILE_EXTENSIONS
import pytest


def locate_file(file_name: str, executing_file: str) -> str:
    """
    Find file relative to a source file, e.g.
    locate("foo/bar.txt", __file__)

    Succeeds regardless to context of execution

    File must exist
    """
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(executing_file)), file_name
    )
    if not os.path.exists(file_path):
        raise TypeError(file_path + " doesn't exist")
    return file_path


def test_with_source_classifier():
    total = 0
    right = 0
    wrong = 0
    try:
        files = locate_file("../../examples/sourceclassifier-master/sources", __file__)
    except TypeError:
        pytest.skip("don't have a bunch of files downloaded to verify against")

    if not os.path.exists(files):
        pytest.skip("don't have a bunch of files downloaded to verify against")

    for subdir, dirs, files in os.walk(files):

        for file_name in files:
            # if not "java" in file_name:
            #     continue
            file_path = subdir + os.sep + file_name
            with open(file_path, encoding="utf-8", errors="ignore") as code_file:
                total += 1
                guess = guess_language_all_methods(code_file.read())
                neither = True
                if guess in ["c", "cpp"] and (
                    file_name.endswith(".gcc") or file_name.endswith(".gcc")
                ):
                    right += 1
                    neither = False
                elif guess in ["php", "xml", "html"] and (
                    file_name.endswith(".php")
                    or file_name.endswith(".xml")
                    or file_name.endswith(".html")
                ):
                    right += 1
                    neither = False
                elif guess in FILE_EXTENSIONS:
                    extensions = FILE_EXTENSIONS[guess]
                    one_does = False
                    for extension in extensions:
                        if file_name.endswith(extension):
                            one_does = True
                    if not one_does:
                        print(file_path, guess)
                        wrong += 1
                        neither = False

                    else:
                        right += 1
                        neither = False

    # 68% !!
    print(f"right {right}... {right/total}%")
    assert right / total > 0.50
