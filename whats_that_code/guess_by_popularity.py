"""Take everyone elses votes. If a vote is for something popular, vote for it in popularity rank"""

from whats_that_code.known_languages import POPULARITY_LIST


def language_by_popularity(guesses: set[str]) -> list[str]:
    """Return the candidate languages that are popular, most-popular first.

    Iterating ``POPULARITY_LIST`` (not the input set) makes the order both
    deterministic — independent of PYTHONHASHSEED, see spec/phase4_notes.md — and
    meaningful: this ballot ranks common languages ahead of rare ones.
    """
    if not guesses:
        return []
    return [language for language in POPULARITY_LIST if language in guesses]
