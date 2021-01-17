"""
Guess by extension
"""
from typing import List

from whats_that_code.known_languages import FILE_EXTENSIONS


def guess_by_extension(file_name: str = "", text: str = "") -> List[str]:
    """
    Guess by extensions
    """
    if not file_name and not text:
        return []

    guesses = set()
    extensions = []
    if file_name:
        extensions.append("." + file_name.split(".")[1])
    if text:
        words = [_ for _ in text.split(" ") if "." in _]
        for word in words:
            if word.endswith("."):
                continue
            extension = word.split(".")[1]
            if 1 < len(extension) < 5:
                extensions.append(extension)

    for key, value in FILE_EXTENSIONS.items():
        for extension in extensions:
            for alternative in value:
                if extension == alternative:
                    guesses.add(key)

    return list(guesses)
