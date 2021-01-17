"""
What programming language is this text
"""
from typing import List, Tuple

from whats_that_code.election import guess_language_all_methods
from whats_that_code.known_languages import FILE_EXTENSIONS

GUESS = None


def assign_extension(all_code: str, tags: List[str]) -> Tuple[str, str]:
    """Guess language and extension"""
    if not all_code:
        return "", ""

    result = guess_language_all_methods(code=all_code, tags=tags)
    if result:
        if result in FILE_EXTENSIONS:
            # take top extension option
            return FILE_EXTENSIONS[result][0], result
        return f".{result}", result

    return "", ""
