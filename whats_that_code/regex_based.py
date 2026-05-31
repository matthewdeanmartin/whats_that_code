"""Detect a language by counting structural regex "markers".

https://github.com/TomCrypto/Codex/blob/master/codex.py

This is the single most expensive voter (profiling shows ~98% of election time is
spent here running ~245 patterns over the text — see spec/phase3_notes.md). The
patterns run on Google's ``re2`` engine — a **core dependency** (``google-re2``) —
which is linear-time and ~6x faster on this workload than stdlib ``re``.

``re2`` is required, but the import is still guarded: if a platform has no re2
wheel the detector degrades to pure ``re`` (identical results, just slower) rather
than failing to import. ``FAST_AVAILABLE`` reflects which engine is live.

Correctness guardrail: ``codex_markers.MARKERS`` (pure ``re``) is the source of
truth. The re2 path must produce *identical* match counts; this is verified on the
corpus by ``test/test_fast/test_regex_fast_parity.py``. The only patterns where
re2 and ``re`` disagree are the two generic ``"code"`` markers, so the ``"code"``
group is always kept on ``re`` (it is excluded from the election by default
anyway). If a future pattern diverges, the parity test fails and the contributor
must keep it on ``re`` here.
"""

from __future__ import annotations

import re
from re import Pattern

from whats_that_code.codex_markers import MARKERS

try:  # core dependency; the guard is a defensive fallback for platforms lacking a wheel
    import re2 as _re2  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - only when the re2 wheel is unavailable
    _re2 = None

FAST_AVAILABLE: bool = _re2 is not None

# Languages kept on pure `re` even in fast mode because re2's match semantics
# differ from Python's for their patterns (verified divergence; see module docs).
# "code" is excluded from the default election, so this never affects public output.
_FORCE_RE_LANGUAGES = frozenset({"code"})


def _to_re2(pattern: Pattern[str]):
    """Recompile a Python ``re`` pattern as a re2 pattern, preserving flags inline."""
    prefix = ""
    if pattern.flags & re.MULTILINE:
        prefix += "m"
    if pattern.flags & re.DOTALL:
        prefix += "s"
    source = (f"(?{prefix})" if prefix else "") + pattern.pattern
    return _re2.compile(source)


def _build_fast_markers() -> dict[str, list]:
    """Mirror MARKERS with re2-compiled patterns, falling back to ``re`` when needed."""
    fast: dict[str, list] = {}
    for language, finders in MARKERS.items():
        if language in _FORCE_RE_LANGUAGES:
            fast[language] = list(finders)
            continue
        compiled = []
        for finder in finders:
            try:
                compiled.append(_to_re2(finder))
            except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
                compiled.append(finder)  # keep pure-re for anything re2 rejects
        fast[language] = compiled
    return fast


_FAST_MARKERS: dict[str, list] | None = _build_fast_markers() if _re2 is not None else None


def language_by_regex_features(text: str, just_code_is_valid: bool = False, use_fast: bool = True) -> list[str]:
    """Count features that signal a language.

    just_code_is_valid — if True, "code" is a valid guess.
    use_fast — use the re2 fast path when available (identical results; for the
        parity test pass ``use_fast=False`` to force the pure-``re`` engine).
    """
    markers = _FAST_MARKERS if (use_fast and _FAST_MARKERS is not None) else MARKERS
    guesses: dict[str, int] = {}
    for language, finders in markers.items():
        if not just_code_is_valid and language == "code":
            continue
        for finder in finders:
            found = finder.findall(text)
            if found:
                guesses[language] = guesses.get(language, 0) + len(found)

    return [language for language, _score in sorted(guesses.items(), key=lambda item: -item[1])]
