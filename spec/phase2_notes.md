# Phase 2 notes — label tiers & rare-language suppression

Recorded 2026-05-31. Phase 2 of `spec/spec.md`: keep every old label, add a rarity
tier to each, and add an **opt-in** way to suppress rare-language matches. The
overriding constraint (2,000 downloads/month) is backwards compatibility: the
default path is byte-for-byte unchanged.

## What was added

- **Rarity tiers in `whats_that_code/languages.py`.** `TIERS = ("rare", "uncommon", "common")` (ordered low→high), `COMMON` / `UNCOMMON` curated
  frozensets, and `tier(name) -> str` / `meets_tier(name, min_tier) -> bool`.
  Anything not in `COMMON` or `UNCOMMON` — including labels outside `CANONICAL`
  (e.g. an arbitrary Pygments lexer name) — is `"rare"`.

  - `COMMON` = the PYPL top-28 (`known_languages.POPULARITY_LIST`) **plus** the
    ubiquitous markup/data/config/shell languages PYPL does not rank (html, css,
    json, xml, yaml, sql, bash, markdown, makefile, docker, ini, toml,
    powershell, batch, sass/scss/less, c). Both spellings of dual-spelled
    languages are listed (e.g. `c#` and `csharp`).
  - `UNCOMMON` = established-but-not-mainstream languages (elixir, erlang,
    clojure, fsharp, ocaml, scheme, racket, elm, crystal, nim, zig, solidity,
    terraform, prolog, fortran, vala, nix, tcl, vhdl/verilog, cmake,
    coffeescript, gdscript, …).
  - `test/test_fast/test_label_registry.py` now asserts `COMMON`/`UNCOMMON` are
    subsets of `CANONICAL` and disjoint.

- **`whats_that_code/options.py`: `@dataclass(frozen=True) Options`.** One opt-in
  knob, `min_tier: str | None = None`, validated in `__post_init__`. This is the
  "typed options object" recommended in `spec/spec.md` §3a: new knobs ride on one
  optional `options=` kwarg instead of growing the positional signature, and there
  is no new heavy dependency (stdlib dataclass, not pydantic).

- **`election.guess_language_all_methods(..., options=None)`.** New trailing
  keyword argument. When `options.min_tier` is set, `_suppress_below_tier()` drops
  below-tier candidates from every ballot **unless** the candidate is backed by
  strong evidence — the union of the extension / shebang / tag / prior votes. So a
  `.zig` file is still Zig even when Zig is "uncommon". `options=None` (the
  default) leaves the ballots untouched; the path is identical to before.

- **`scripts/evaluate.py --min-tier {common,uncommon,rare}`** so the suppression's
  accuracy effect is a harness number, not a guess. The recorded baseline
  (`spec/eval_baseline.json`) is always `min_tier=None`.

## Why suppression is *only* removal, and only of ballots

The election is instant-runoff over per-voter ballots. Suppression filters
candidates out of the ballots before the vote; it never adds, re-weights, or
reorders. That makes it impossible for suppression to *introduce* a wrong answer
that wasn't already reachable — it can only refuse a below-tier candidate or shift
the runoff among the survivors. Strong-evidence candidates are exempt because an
extension/shebang/tag is high-precision: a rare language with a matching `.zig`
extension should win regardless of rarity.

## Measured effect (Linguist samples, `--limit 20`, test split, seed 0)

| Axis | default | `--min-tier common` |
|------|---------|---------------------|
| code only (strict) | 13.0% | 11.3% |
| with filename (strict) | 48.0% | 48.0% |

Reading: **with-filename is unchanged** — extension evidence is exempt, so the
common real-world call is unaffected. **Code-only drops** because the Linguist
corpus is heavy with rare languages; refusing to guess them lowers raw accuracy on
*this* corpus. That is the intended precision/recall trade — callers who never want
a rare guess accept lower recall on rare inputs. On a corpus dominated by common
languages the effect would be the opposite (fewer rare false positives).

## Caveat: don't over-read per-language deltas in the suppressed run

A `--min-tier common` run can show a *common* language (e.g. `haskell`, n=1)
apparently regressing to 0%. That is **not** suppression dropping a common label
(verified: `tier("haskell") == "common"`, and the file still classifies as
`haskell` when run in isolation). It is the `pyrankvote` unseeded-`random`
tie-break (phase0 finding #6): the harness seeds `random` once and processes ~1100
files in sequence, so changing the candidate sets earlier in the run consumes the
RNG stream differently and flips a downstream tie. The recommended deterministic-
election fix (sort vote lists + stable tie-break) would remove this noise and make
suppressed/unsuppressed per-language diffs trustworthy. Until then, trust the
aggregate and the isolated-file checks, not single-sample per-language deltas.

## How to add a new language (the additive recipe)

1. Add its label to `languages.CANONICAL` (lowercase, no dot).
1. Give it data in at least one table — usually `known_languages.FILE_EXTENSIONS`
   (extension) and/or `tags_data.RELATED_TAGS` (tag). Regex/keyword markers are
   optional.
1. Assign a tier: add it to `COMMON` or `UNCOMMON` in `languages.py`, or leave it
   out for `"rare"`. Tier choice only affects the opt-in suppression path, so it is
   safe to revise later with the harness (Phase 4).
1. `make api-check` and the characterization test must stay green; emitted
   spellings of existing labels never change.
