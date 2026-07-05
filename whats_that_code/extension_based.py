"""Guess by extension"""

import fnmatch
import os

from whats_that_code.known_languages import FILE_EXTENSIONS


def guess_by_extension(file_name: str = "", text: str = "") -> list[str]:
    """Guess by extensions"""
    if not file_name and not text:
        return []
    # Some language-defining filenames do not have a conventional extension
    # (Dockerfile, CMakeLists.txt), while others are commonly suffixed variants
    # (.env.example, .env.local).  FILE_EXTENSIONS has historically contained
    # exact filenames and glob patterns for these cases, so consider the basename
    # as well as the suffix.
    basename = file_name.replace("\\", "/").rsplit("/", 1)[-1]
    _, extension_part = os.path.splitext(file_name)

    guesses: set[str] = set()
    extensions = []
    if file_name:
        extensions.append(extension_part)
    if text:
        words = [_ for _ in text.split(" ") if "." in _]
        for word in words:
            if word.endswith("."):
                continue
            _, extension = os.path.splitext(word)
            if 1 < len(extension) < 5:
                extensions.append(extension)

    for key, value in FILE_EXTENSIONS.items():
        filename_matches = any(
            basename == alternative or fnmatch.fnmatchcase(basename, alternative) for alternative in value
        )
        if basename and filename_matches:
            guesses.add(key)
        for extension in extensions:
            for alternative in value:
                if extension == alternative:
                    guesses.add(key)

    # sorted (not list(set)) so ballot order is deterministic regardless of
    # PYTHONHASHSEED — see spec/phase4_notes.md (deterministic election).
    return sorted(guesses)
