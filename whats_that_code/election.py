"""Ranked choice election"""

import pyrankvote
from pyrankvote import Ballot, Candidate

from whats_that_code.extension_based import guess_by_extension
from whats_that_code.guess_by_popularity import language_by_popularity
from whats_that_code.keyword_based import guess_by_keywords
from whats_that_code.known_languages import FILE_EXTENSIONS
from whats_that_code.languages import meets_tier
from whats_that_code.options import Options
from whats_that_code.parsing_based import parses_as_xml
from whats_that_code.pygments_based import language_by_pygments
from whats_that_code.regex_based import language_by_regex_features
from whats_that_code.shebang_based import language_by_shebang
from whats_that_code.tag_based import match_tag_to_languages


def guess_language_all_methods(
    code: str,
    file_name: str = "",
    surrounding_text: str = "",
    tags: list[str] | None = None,
    priors: list[str] | None = None,
    options: Options | None = None,
) -> str | None:
    """
    Choose language with multiple algorithms via ranked choice.

    Ensemble classifier in fancy talk.

    ``options`` is an opt-in :class:`whats_that_code.options.Options`. The default
    (``None``) reproduces today's behavior exactly; passing
    ``Options(min_tier="common")`` suppresses rare-language candidates unless they
    are backed by strong evidence (extension/shebang/tag/prior).
    """

    # very smart voters
    vote_by_shebang = language_by_shebang(code)
    vote_by_extension = guess_by_extension(file_name=file_name)
    vote_by_extension_in_text = guess_by_extension(text=surrounding_text)
    vote_by_tags = match_tag_to_languages(tags or [])

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
    vote_by_pygments = [_ for _ in language_by_pygments(code) if _ not in vote_by_keyword]

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
    )
    # above keeps wanting to guess the obscure languages.
    vote_by_popularity = language_by_popularity(all_possible)

    all_vote_lists = [
        # if this has any info, it probably is really good. Give 'em two votes
        vote_by_tags,
        vote_by_shebang,
        vote_by_extension,
        vote_by_extension_in_text,
        # ad hoc way to give smart algos more votes
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

    # Opt-in rare-language suppression. Default (options is None / min_tier None)
    # leaves the ballots untouched, so behavior is identical to before. When a
    # min_tier is set we drop below-tier candidates from every ballot — but never
    # those backed by strong evidence (a matching extension/shebang/tag/prior),
    # so a `.zig` file is still Zig even when Zig is "rare".
    if options is not None and options.min_tier is not None:
        strong_evidence = set(
            vote_by_tags + vote_by_shebang + vote_by_extension + vote_by_extension_in_text + vote_by_priors
        )
        _suppress_below_tier(all_vote_lists, options.min_tier, strong_evidence)

    # validate votes, get list of everything voted for
    for votes in all_vote_lists:
        for item in votes:
            all_possible.add(item)
        for vote in votes:
            if vote.lower() != vote:
                raise TypeError("Bad casing")
            if "." in vote:
                raise TypeError("Name not extension")

    # handle xml & php
    can_be_xml = True
    if "xml" in all_possible and not parses_as_xml(code):
        for votes in all_vote_lists:
            if "xml" in votes:
                votes.remove("xml")
                can_be_xml = False

    # convert to ballots and hold election
    candidates: dict[str, Candidate] = {}
    ballots = []
    for ballot in all_vote_lists:
        for candidate in ballot:
            candidates[candidate] = Candidate(candidate)
        if ballot:
            ranked_ballot = Ballot(ranked_candidates=[candidates[_] for _ in ballot])
            ballots.append(ranked_ballot)
        # else abstains

    if len(candidates) == 1:
        return next(iter(candidates.values())).name

    election_result = pyrankvote.instant_runoff_voting(list(candidates.values()), ballots)

    winners = election_result.get_winners()
    if not winners:
        return None

    if not can_be_xml and winners[0].name == "xml":
        raise TypeError()
    return winners[0].name


def _suppress_below_tier(vote_lists: list[list[str]], min_tier: str, strong_evidence: set[str]) -> None:
    """Drop below-``min_tier`` candidates from each ballot, in place.

    A candidate survives if it is at least as common as ``min_tier`` *or* it
    appears in ``strong_evidence`` (the extension/shebang/tag/prior votes). The
    lists are mutated in place; the same list object may appear more than once in
    ``vote_lists`` (smart voters are double-weighted) — re-filtering it is
    idempotent, so that is safe.
    """
    for votes in vote_lists:
        votes[:] = [v for v in votes if v in strong_evidence or meets_tier(v, min_tier)]


def guess_by_prior_knowledge(priors: list[str] | None) -> list[str]:
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
