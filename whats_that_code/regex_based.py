"""Fast detect Python via regex markers.

https://github.com/TomCrypto/Codex/blob/master/codex.py
"""

from whats_that_code.codex_markers import MARKERS


def language_by_regex_features(text: str, just_code_is_valid: bool = False) -> list[str]:
    """Count features that signal a language.

    just_code_is_valid — if True, "code" is a valid guess.
    """
    guesses: dict[str, int] = {}
    for language, finders in MARKERS.items():
        if not just_code_is_valid and language == "code":
            continue
        for finder in finders:
            found = finder.findall(text)
            if found:
                guesses[language] = guesses.get(language, 0) + len(found)

    return [language for language, _score in sorted(guesses.items(), key=lambda item: -item[1])]
