"""
Guess by SO Tag
"""
from typing import Dict, List

from whats_that_code.known_languages import FILE_EXTENSIONS

RELATED_TAGS: Dict[str, List[str]] = {"python": ["pandas", "numpy"]}


def match_tag_to_languages(tags: List[str]) -> List[str]:
    """Guess language by tag"""
    if not tags:
        return []
    guesses = set()
    for tag in (_.lower() for _ in tags):
        if not tag:
            continue
        if tag in FILE_EXTENSIONS:
            guesses.add(tag)

    # TODO: add strength of relation & sort guesses by strength
    if not guesses:
        for tag in tags:
            for key, value in RELATED_TAGS.items():
                if tag in value:
                    guesses.add(key)

    return list(guesses)


# Old algo
# def match_tag_to_language(tags: List[str]) -> Optional[Tuple[str, str]]:
#     """Guess language by tag"""
#     for tag in (_.lower() for _ in tags):
#         if not tag:
#             continue
#         if tag in FILE_EXTENSIONS:
#             return FILE_EXTENSIONS[tag], tag
#     return None
