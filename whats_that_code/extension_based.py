"""
Guess by extension
"""
import os
from typing import List

from whats_that_code.known_languages import FILE_EXTENSIONS


def guess_by_extension(file_name: str = "", text: str = "") -> List[str]:
    """
    Guess by extensions
    """
    if not file_name and not text:
        return []
    _, extension_part = os.path.splitext(file_name)

    if not extension_part:
        return []

    guesses = set()
    extensions = []
    if file_name:
        # TODO: use
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
        for extension in extensions:
            for alternative in value:
                if extension == alternative:
                    guesses.add(key)

    return list(guesses)
