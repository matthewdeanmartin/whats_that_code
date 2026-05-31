"""The re2 fast path must produce identical results to pure `re` (Phase 3).

``codex_markers.MARKERS`` (pure ``re``) is the source of truth; the core
``google-re2`` dependency runs the same patterns on Google's ``re2`` engine for
speed. This test is the guardrail proving the swap does not change answers: for
every election-relevant pattern, re2 and ``re`` must return the same match count on
every corpus snippet. Skips only on the rare platform with no re2 wheel (the
defensive pure-``re`` fallback).
"""

from pathlib import Path

import pytest

from whats_that_code.codex_markers import MARKERS
from whats_that_code.regex_based import (
    _FORCE_RE_LANGUAGES,
    FAST_AVAILABLE,
    _build_fast_markers,
    language_by_regex_features,
)

pytestmark = pytest.mark.skipif(not FAST_AVAILABLE, reason="google-re2 ([fast] extra) not installed")

REPO = Path(__file__).resolve().parent.parent.parent
CHAR_CORPUS = REPO / "test" / "data" / "characterization"


def _corpus_texts() -> list[str]:
    texts = []
    for path in sorted(CHAR_CORPUS.rglob("*")):
        if path.is_file() and path.name != "expected.json":
            texts.append(path.read_text(encoding="utf-8", errors="ignore"))
    # always include a few tricky strings even if the corpus is missing
    texts += ["", "x = 1\n", "#include <stdio.h>\nint main(){}\n", "<a href='x'>y</a>"]
    return texts


def test_re2_match_counts_match_re_for_election_patterns():
    """Every non-'code' pattern returns identical findall counts under re2 and re."""
    fast = _build_fast_markers()
    mismatches = []
    for text in _corpus_texts():
        for language, re_finders in MARKERS.items():
            if language in _FORCE_RE_LANGUAGES:
                continue  # kept on `re` deliberately; not used by the default election
            for idx, re_finder in enumerate(re_finders):
                a = len(re_finder.findall(text))
                b = len(fast[language][idx].findall(text))
                if a != b:
                    mismatches.append((language, idx, re_finder.pattern, a, b))
    assert not mismatches, f"re2 diverged from re on: {mismatches[:5]} (+{len(mismatches) - 5} more)"


def test_force_re_languages_stay_on_re():
    """The known-divergent 'code' patterns must not be re2-compiled."""
    fast = _build_fast_markers()
    for language in _FORCE_RE_LANGUAGES:
        assert fast[language] == MARKERS[language]


def test_fast_and_slow_paths_agree_on_language_list():
    """The public function returns the same ranking with and without the fast path."""
    for text in _corpus_texts():
        assert language_by_regex_features(text, use_fast=True) == language_by_regex_features(text, use_fast=False)
