"""Opt-in options for the language election (spec/spec.md Phase 2).

A single frozen, validated options object keeps the public signature of
:func:`whats_that_code.election.guess_language_all_methods` stable while still
allowing new knobs: callers pass one optional ``options=Options(...)`` keyword
argument rather than the signature growing positional parameters over time
(see spec/spec.md §3a).

The default ``Options()`` reproduces today's behavior exactly — every field
defaults to "no change". New knobs added in later phases must keep that property.
"""

from __future__ import annotations

from dataclasses import dataclass

from whats_that_code.languages import TIERS


@dataclass(frozen=True)
class Options:
    """Optional, opt-in tuning for :func:`guess_language_all_methods`.

    Attributes:
        min_tier: If set to ``"common"`` or ``"uncommon"``, candidate languages
            whose rarity tier is below it are excluded from the election *unless*
            there is strong evidence for them (a matching file extension, shebang,
            tag, or caller-supplied prior). This is the "don't match on rare
            languages" feature. ``None`` (the default) applies no suppression, so
            the result is identical to calling the function without options.
        use_parsers: If True, also identify the language by actually parsing the
            code (the "parser trick", see ``whats_that_code.parser_detect``):
            stdlib validators (python/json/xml/toml) always, plus many more
            grammars when the ``whats_that_code[fast]`` extra is installed. A clean
            parse is treated as strong evidence. ``False`` (the default) never runs
            parsers, so the result is identical to calling without options.
    """

    min_tier: str | None = None
    use_parsers: bool = False

    def __post_init__(self) -> None:
        if self.min_tier is not None and self.min_tier not in TIERS:
            raise ValueError(f"min_tier must be one of {TIERS} or None, got {self.min_tier!r}")
