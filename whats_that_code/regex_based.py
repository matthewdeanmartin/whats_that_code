"""
Fast detect python.

https://github.com/TomCrypto/Codex/blob/master/codex.py
"""
from typing import Dict, List

from whats_that_code.codex_markers import MARKERS


def language_by_regex_features(
    text: str, just_code_is_valid: bool = False
) -> List[str]:
    """Count features that signal python, multiples
    worth extra only for 2nd.
    just_code_is_valid - if True, "code" is a valid guess.
    """

    guesses: Dict[str, int] = {}
    for language, finders in MARKERS.items():
        if not just_code_is_valid and language == "code":
            continue
        for finder in finders:
            found = finder.findall(text)
            if len(found) > 0:
                if language in guesses:
                    guesses[language] += len(found)
                else:
                    guesses[language] = len(found)

    results = [
        language
        for language, score in sorted(guesses.items(), key=lambda item: -item[1])
    ]
    return results
