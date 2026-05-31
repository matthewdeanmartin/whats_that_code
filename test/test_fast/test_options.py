"""Tests for opt-in Options + rare-language suppression (spec/spec.md Phase 2).

The overriding constraint is backwards compatibility: the default path
(no ``options`` / ``Options()``) must behave exactly as before. The new
``min_tier`` knob only ever *removes* obscure candidates, and never a candidate
backed by strong evidence (a matching extension/shebang/tag/prior).
"""

import dataclasses
import random

import pytest

from whats_that_code.election import _suppress_below_tier, guess_language_all_methods
from whats_that_code.languages import TIERS, meets_tier, tier
from whats_that_code.options import Options

# Snippets whose code-only guess varies by interpreter/seed, used to assert the
# tier *invariant* (never returns something below the requested tier) rather than
# a specific label — the specific label is nondeterministic (see phase0 findings).
CODE_ONLY_SNIPPETS = [
    "(defun fact (n) (if (= n 0) 1 (* n (fact (- n 1)))))",
    "fact(0,1).\nfact(N,F):-N>0,M is N-1,fact(M,G),F is N*G.",
    "(define (square x) (* x x))",
    "proc add {a b} { expr {$a + $b} }",
    "1 2 + . cr",
]


# ── Options dataclass ────────────────────────────────────────────────────────


def test_options_default_is_no_suppression():
    assert Options().min_tier is None


@pytest.mark.parametrize("value", [None, "common", "uncommon", "rare"])
def test_options_accepts_valid_min_tier(value):
    assert Options(min_tier=value).min_tier == value


def test_options_rejects_invalid_min_tier():
    with pytest.raises(ValueError):
        Options(min_tier="bogus")


def test_options_is_frozen():
    opts = Options(min_tier="common")
    with pytest.raises(dataclasses.FrozenInstanceError):
        opts.min_tier = "rare"  # type: ignore[misc]


# ── Tier helpers ─────────────────────────────────────────────────────────────


def test_tier_classification():
    assert tier("python") == "common"  # PYPL
    assert tier("json") == "common"  # ubiquitous, non-PYPL
    assert tier("zig") == "uncommon"
    assert tier("befunge") == "rare"
    assert tier("not-a-language-at-all") == "rare"  # unknown -> rare


def test_meets_tier_ordering():
    assert meets_tier("python", "common")
    assert meets_tier("zig", "uncommon")
    assert not meets_tier("zig", "common")  # uncommon < common
    assert not meets_tier("befunge", "uncommon")
    assert meets_tier("befunge", "rare")  # everything meets the lowest bar
    assert tuple(TIERS) == ("rare", "uncommon", "common")


# ── _suppress_below_tier helper (deterministic, no election randomness) ───────


def test_suppress_drops_below_tier_keeps_evidence():
    keyword_votes = ["python", "zig", "scheme"]  # uncommon + uncommon, no evidence
    extension_votes = ["befunge"]  # strong evidence for an otherwise-rare lang
    vote_lists = [extension_votes, keyword_votes]
    _suppress_below_tier(vote_lists, "common", strong_evidence={"befunge"})
    assert keyword_votes == ["python"]  # zig + scheme (below common) dropped
    assert extension_votes == ["befunge"]  # evidence-backed rare lang survives


def test_suppress_keeps_evidenced_candidate_in_every_ballot():
    """strong_evidence is global: an evidenced label survives wherever it appears."""
    extension_votes = ["befunge"]
    keyword_votes = ["python", "befunge"]
    _suppress_below_tier([extension_votes, keyword_votes], "common", strong_evidence={"befunge"})
    assert keyword_votes == ["python", "befunge"]


def test_suppress_is_idempotent_on_shared_list():
    """Smart voters appear twice in the ballot list; re-filtering must be safe."""
    shared = ["python", "zig"]
    vote_lists = [shared, shared]  # same object twice, like the real election
    _suppress_below_tier(vote_lists, "common", strong_evidence=set())
    assert shared == ["python"]


def test_suppress_uncommon_tier_keeps_uncommon():
    votes = ["python", "zig", "befunge"]
    _suppress_below_tier([votes], "uncommon", strong_evidence=set())
    assert votes == ["python", "zig"]  # only befunge (rare) dropped


# ── End-to-end: defaults are sacred ──────────────────────────────────────────


def test_default_path_is_unchanged_by_empty_options():
    for snippet in [*CODE_ONLY_SNIPPETS, "def f():\n    return 1\n"]:
        random.seed(0)
        without = guess_language_all_methods(snippet)
        random.seed(0)
        with_none = guess_language_all_methods(snippet, options=None)
        random.seed(0)
        with_default = guess_language_all_methods(snippet, options=Options())
        assert without == with_none == with_default


# ── End-to-end: suppression never returns something below the tier ───────────


def test_min_tier_common_never_returns_rare_on_code():
    for snippet in CODE_ONLY_SNIPPETS:
        random.seed(0)
        result = guess_language_all_methods(snippet, options=Options(min_tier="common"))
        assert result is None or tier(result) == "common", f"{snippet!r} -> {result!r}"


def test_min_tier_uncommon_never_returns_rare_on_code():
    for snippet in CODE_ONLY_SNIPPETS:
        random.seed(0)
        result = guess_language_all_methods(snippet, options=Options(min_tier="uncommon"))
        assert result is None or meets_tier(result, "uncommon"), f"{snippet!r} -> {result!r}"


def test_suppression_actually_changes_some_answer():
    """At least one snippet whose unsuppressed guess is rare flips under min_tier."""
    flipped = []
    for snippet in CODE_ONLY_SNIPPETS:
        random.seed(0)
        base = guess_language_all_methods(snippet)
        random.seed(0)
        suppressed = guess_language_all_methods(snippet, options=Options(min_tier="common"))
        if base is not None and tier(base) == "rare":
            assert suppressed is None or tier(suppressed) == "common"
            flipped.append((snippet, base, suppressed))
    assert flipped, "expected at least one rare code-only guess to be suppressed"


# ── End-to-end: strong evidence overrides suppression ────────────────────────


def test_extension_evidence_survives_common_suppression():
    """A .zig file is Zig even though Zig is below 'common'."""
    random.seed(0)
    assert guess_language_all_methods("const x = 1;\n", file_name="x.zig") == "zig"
    random.seed(0)
    assert guess_language_all_methods("const x = 1;\n", file_name="x.zig", options=Options(min_tier="common")) == "zig"


def test_rare_extension_evidence_survives_common_suppression():
    """An extension match for a *rare* language is honored under suppression."""
    random.seed(0)
    assert guess_language_all_methods("1 2 + . @", file_name="x.befunge", options=Options(min_tier="common")) == (
        "befunge"
    )
