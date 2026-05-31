"""Take everyone elses votes. If a vote is for something popular, vote for it in popularity rank"""

from whats_that_code.known_languages import POPULARITY_LIST


def language_by_popularity(guesses: set[str]) -> list[str]:
    """Guess by popularity rank among candidates"""
    if not guesses:
        return []
    return [guess for guess in guesses if guess in POPULARITY_LIST]
