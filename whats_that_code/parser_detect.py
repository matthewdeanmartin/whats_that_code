"""Identify languages by actually parsing the code (spec/spec.md Phase 3).

The "parser trick": if code parses cleanly under language X's grammar, that is
strong evidence it is X. Two layers:

* **stdlib validators** (always available, no extra): Python (``ast``), JSON,
  XML (``lxml``), and TOML (``tomllib`` on 3.11+). See ``parsing_based``.
* **tree-sitter grammars** (optional ``whats_that_code[fast]`` extra): dozens of
  real grammars via ``tree-sitter-language-pack``, used to confirm/disambiguate
  many more languages (go, rust, ruby, java, …) that have no stdlib parser.

This whole module is **opt-in**: it only runs when a caller passes
``Options(use_parsers=True)``. The default election never calls it, so default
answers are unchanged.

Two hard lessons baked into the design (see spec/phase3_notes.md):

1. *Clean-parse is permissive.* Grammars like PHP / HTML / YAML accept almost any
   text, so they are excluded — only discriminative grammars are in
   :data:`_GRAMMARS`. Even so, the correct language is reliably *present* in the
   clean set (with a few benign overlaps the election's clone groups absorb).
2. *Restrict to candidates when possible.* When the election already has candidate
   languages, we only test those grammars — turning the parser into a precise
   disambiguator rather than a noisy from-scratch guesser.

The tree-sitter binding shipped by the language pack is non-standard (accessors are
methods, ``parse`` wants ``str``); a capability probe at import confirms it works
and disables it gracefully otherwise, so a broken/absent binding silently falls
back to the stdlib validators.
"""

from __future__ import annotations

from typing import Any

from whats_that_code.languages import COMMON, UNCOMMON, canonical
from whats_that_code.parsing_based import parses_as_json, parses_as_python, parses_as_toml, parses_as_xml

# Canonical label -> tree-sitter-language-pack grammar name. Curated to grammars
# that *reject* other languages reasonably well. Deliberately excludes permissive
# grammars (php, html, yaml, markdown, css) and languages better served by the
# stdlib validators (python, json, xml, toml). Add a language only after checking
# it does not clean-parse unrelated code.
_GRAMMARS: dict[str, str] = {
    "go": "go",
    "rust": "rust",
    "c": "c",
    "c++": "cpp",
    "java": "java",
    "javascript": "javascript",
    "typescript": "typescript",
    "ruby": "ruby",
    "lua": "lua",
    "bash": "bash",
    "kotlin": "kotlin",
    "swift": "swift",
    "scala": "scala",
    "haskell": "haskell",
    "sql": "sql",
    "c#": "csharp",
    "perl": "perl",
    "r": "r",
    "julia": "julia",
    "elixir": "elixir",
    "erlang": "erlang",
    "ocaml": "ocaml",
    "dart": "dart",
    "solidity": "solidity",
    "zig": "zig",
    "clojure": "clojure",
}

# Stdlib validators run for these labels (no extra needed). Order is the emit order.
_STDLIB: dict[str, object] = {
    "python": parses_as_python,
    "json": parses_as_json,
    "xml": parses_as_xml,
    "toml": parses_as_toml,
}


def _call(value):
    """The language-pack binding exposes accessors as methods; normalize that."""
    return value() if callable(value) else value


def _make_tree_sitter():
    """Return a ``clean(label, code) -> bool`` closure, or None if unusable."""
    try:
        from tree_sitter_language_pack import get_parser  # pylint: disable=import-outside-toplevel
    except ImportError:
        return None

    parsers: dict[str, Any] = {}

    def _clean(label: str, code: str) -> bool:
        grammar = _GRAMMARS.get(label)
        if grammar is None:
            return False
        parser = parsers.get(grammar)
        if parser is None:
            try:
                parser = get_parser(grammar)
            except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
                return False
            parsers[grammar] = parser
        try:
            tree = parser.parse(code)
            if tree is None:
                return False
            root = _call(tree.root_node)
            has_error = _call(root.has_error)
            child_count = _call(root.child_count)
            return (not has_error) and child_count > 0
        except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
            return False

    # Capability probe: the binding must agree that valid code parses cleanly and
    # obvious garbage does not (use a grammar that is actually in _GRAMMARS — "go"
    # is strict and present). If the binding misbehaves, disable tree-sitter so we
    # fall back to the stdlib validators.
    try:
        if _clean("go", "package main\nfunc main() {}\n") and not _clean("go", ")(}{ ?? !! <<<<"):
            return _clean
    except Exception:  # pylint: disable=broad-exception-caught  # pragma: no cover
        return None
    return None


_TS_CLEAN = _make_tree_sitter()
TREE_SITTER_AVAILABLE: bool = _TS_CLEAN is not None


def detect_by_parsing(code: str, candidates: set[str] | None = None) -> list[str]:
    """Return canonical languages that ``code`` provably parses as.

    stdlib validators always run. tree-sitter grammars run too when the extra is
    installed: restricted to ``candidates`` when given (precise disambiguation),
    otherwise across the full curated strict set (broader identification). Results
    are deduped, stdlib-first.
    """
    if not code or not code.strip():
        return []

    found: list[str] = []

    def _add(label: str) -> None:
        norm = canonical(label)
        if norm not in found:
            found.append(norm)

    for label, validator in _STDLIB.items():
        if candidates is not None and canonical(label) not in candidates:
            continue
        if validator(code):  # type: ignore[operator]
            _add(label)

    if _TS_CLEAN is not None:
        if candidates is not None:
            grammars_to_try = [lbl for lbl in _GRAMMARS if canonical(lbl) in candidates]
        else:
            # No candidates: only attempt grammars for languages we'd actually emit
            # (common/uncommon) to keep the noise down on the from-scratch path.
            grammars_to_try = [lbl for lbl in _GRAMMARS if canonical(lbl) in COMMON | UNCOMMON]
        for label in grammars_to_try:
            if _TS_CLEAN(label, code):
                _add(label)

    return found
