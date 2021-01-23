"""
Ranked choice election
"""
from typing import List, Optional

import pyrankvote
from pyrankvote import Ballot, Candidate

from whats_that_code.extension_based import guess_by_extension
from whats_that_code.guess_by_popularity import language_by_popularity
from whats_that_code.keyword_based import guess_by_keywords
from whats_that_code.known_languages import FILE_EXTENSIONS
from whats_that_code.parsing_based import parses_as_xml
from whats_that_code.pygments_based import language_by_pygments
from whats_that_code.regex_based import language_by_regex_features
from whats_that_code.shebang_based import language_by_shebang
from whats_that_code.tag_based import match_tag_to_languages


def guess_language_all_methods(
    code: str,
    file_name: str = "",
    surrounding_text: str = "",
    tags: Optional[List[str]] = None,
    priors: Optional[List[str]] = None,
) -> Optional[str]:
    """
    Choose language with multiple algorithms via ranked choice.

    Ensemble classifier in fancy talk.
    """

    # very smart voters
    vote_by_shebang = language_by_shebang(code)
    vote_by_extension = guess_by_extension(file_name=file_name)
    vote_by_extension_in_text = guess_by_extension(text=surrounding_text)
    vote_by_tags = match_tag_to_languages(tags)

    # mid-tier voters
    vote_by_priors = guess_by_prior_knowledge(priors)
    vote_by_regex_features = language_by_regex_features(code)

    all_but_stupid = set(
        vote_by_tags
        + vote_by_shebang
        + vote_by_extension
        + vote_by_extension_in_text
        + vote_by_regex_features
        + vote_by_priors
    )
    # stupid voters
    vote_by_keyword = guess_by_keywords(code)
    # dumb voter block can't double their impact
    vote_by_pygments = [
        _ for _ in language_by_pygments(code) if _ not in vote_by_keyword
    ]

    # Only want to hear from stupid voters if no one else votes
    if all_but_stupid:
        vote_by_keyword = []
        vote_by_pygments = []

    all_possible = set(
        vote_by_tags
        + vote_by_shebang
        + vote_by_extension
        + vote_by_extension_in_text
        + vote_by_regex_features
        + vote_by_priors
        # don't include stupid voters
    )
    # above keeps wanting to guess the obscure languages.
    vote_by_popularity = language_by_popularity(all_possible)

    all_vote_lists = [
        # if this has any info, in probably is really good. Give 'em two votes
        vote_by_tags,
        vote_by_shebang,
        vote_by_extension,
        vote_by_extension_in_text,
        # ad hoc way to give smart algo's more votes
        vote_by_tags,
        vote_by_shebang,
        vote_by_extension,
        vote_by_extension_in_text,
        # mid tier
        vote_by_priors,
        vote_by_regex_features,
        vote_by_popularity,
        # dummies
        vote_by_keyword,
        vote_by_pygments,
    ]

    # validate votes, get list of everything voted for
    for votes in all_vote_lists:
        for item in votes:
            all_possible.add(item)
        for vote in votes:
            if vote.lower() != vote:
                raise TypeError("Bad casing")
            if "." in vote:
                raise TypeError("Name not extension")

    # TODO: more comprehensive way to deal with "clones"
    # handle xml & php
    can_be_xml = True
    if "xml" in all_possible:
        if not parses_as_xml(code):
            for votes in all_vote_lists:
                if "xml" in votes:
                    votes.remove("xml")
                    can_be_xml = False

    # convert to ballots and hold election
    candidates = {}
    ballots = []
    for ballot in all_vote_lists:
        for candidate in ballot:
            candidates[candidate] = Candidate(candidate)
        if ballot:
            ranked_ballot = Ballot(ranked_candidates=[candidates[_] for _ in ballot])
            ballots.append(ranked_ballot)
        # else abstains

    if len(candidates) == 1:
        return list(candidates.values())[0].name

    election_result = pyrankvote.instant_runoff_voting(
        list(candidates.values()), ballots
    )

    winners = election_result.get_winners()
    if not winners:
        return None

    if not can_be_xml and winners[0].name == "xml":
        raise TypeError()
    return winners[0].name


def guess_by_prior_knowledge(priors: Optional[List[str]]) -> List[str]:
    """Let user tell us what he thinks are likely"""
    vote_by_priors = []
    if priors:
        for prior in priors:
            if prior in FILE_EXTENSIONS:
                if prior not in vote_by_priors:
                    vote_by_priors.append(prior)
            else:
                print(f"{prior} is not a known programming language")
    return vote_by_priors
