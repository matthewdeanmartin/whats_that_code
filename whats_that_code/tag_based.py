"""Guess by SO Tag"""

from whats_that_code.known_languages import FILE_EXTENSIONS
from whats_that_code.tags_data import RELATED_TAGS


def match_tag_to_languages(tags: list[str]) -> list[str]:
    """Guess language by tag"""
    if not tags:
        return []
    # e.g. tagged python, then guess python
    strong_guesses: set[str] = set()
    for tag in (_.lower() for _ in tags):
        if not tag:
            continue
        if tag in FILE_EXTENSIONS:
            strong_guesses.add(tag)

    # e.g. tagged numpy, which is commonly related to python
    weak_guesses: set[str] = set()
    for tag in tags:
        for key, value in RELATED_TAGS.items():
            if tag in value[0:3]:
                weak_guesses.add(key)

    new_weak_guesses = [guess for guess in weak_guesses if guess not in strong_guesses]
    return list(strong_guesses) + new_weak_guesses
