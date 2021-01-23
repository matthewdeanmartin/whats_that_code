"""
Guess by SO Tag
"""
from typing import List

from whats_that_code.known_languages import FILE_EXTENSIONS
from whats_that_code.tags_data import RELATED_TAGS


def match_tag_to_languages(tags: List[str]) -> List[str]:
    """Guess language by tag"""
    if not tags:
        return []
    # eg. tagged python, then guess python
    strong_guesses = set()
    for tag in (_.lower() for _ in tags):
        if not tag:
            continue
        if tag in FILE_EXTENSIONS:
            strong_guesses.add(tag)

    # e.g. tagged, numpy, which is commonly related to python
    weak_guesses = set()
    for tag in tags:
        for key, value in RELATED_TAGS.items():
            if tag in value[0:3]:
                weak_guesses.add(key)

    new_weak_guesses = []
    for guess in weak_guesses:
        if guess not in strong_guesses:
            new_weak_guesses.append(guess)
    return list(strong_guesses) + list(new_weak_guesses)


# Old algo
# def match_tag_to_language(tags: List[str]) -> Optional[Tuple[str, str]]:
#     """Guess language by tag"""
#     for tag in (_.lower() for _ in tags):
#         if not tag:
#             continue
#         if tag in FILE_EXTENSIONS:
#             return FILE_EXTENSIONS[tag], tag
#     return None
