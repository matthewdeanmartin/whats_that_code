"""
Take everyone elses votes. If a vote is for something popular, vote for it in popularity
rank
"""
from typing import List, Set

from whats_that_code.known_languages import POPULARITY, POPULARITY_LIST


def language_by_popularity(guesses: Set[str]) -> List[str]:
    """Guess by parsing"""
    if not guesses:
        return []
    votes = []
    for guess in guesses:
        if guess in POPULARITY_LIST:
            votes.append(guess)
    return votes
