# Phase 3 notes — performance & the parser trick

Recorded 2026-05-31. Phase 3 of `spec/spec.md`: make detection faster without
changing default answers, add an optional fast-parser extra, and use parsing to
identify more languages. As always the default path is unchanged (verified: the
`spec/eval_baseline.json` diff stays all `=` and the characterization test is
green for every change below).

## Profile first (the rule paid off)

`scripts/bench.py` (`make bench`) profiles `guess_language_all_methods` over a
corpus sample and reports import time + median/p95 latency + cProfile hot spots.

The profiler **overturned the spec's stated suspicion** that `pygments.guess_lexer`
was the bottleneck. The real cost is `regex_based.language_by_regex_features`:
~98% of runtime, ~148k `re.findall` calls over ~245 codex marker patterns.
Pygments was 0.12s of 21s. *No optimization was chosen until this number existed.*

## What changed

### 1. Lazy dumb voters (pure-python, identical answers)

`election.py` used to always compute `guess_by_keywords` and
`pygments.guess_lexer`, then *discard* them whenever a smart voter (extension/
shebang/tag/regex/prior) had already spoken. Now they are only computed when no
smart voter spoke. The discarded votes never affected the result, so answers are
identical — it just stops doing wasted work on the common (with-filename) path.

### 2. re2 fast regex engine (core dependency, identical answers)

`regex_based.py` runs the codex markers on Google's linear-time `re2` engine.
`google-re2` is a **core dependency** (promoted from the `[fast]` extra on
2026-05-31 — the regex path is the detector's bottleneck, so everyone gets the
speedup), but the import is guarded: a platform with no re2 wheel falls back to
pure `re` (identical results, slower). `codex_markers.MARKERS` (pure `re`) stays
the source of truth.

- **Correctness:** across the corpus, re2 and `re` returned identical match counts
  for **every** election-relevant pattern. The only two divergent patterns are the
  generic `"code"` markers (which the default election excludes anyway), so the
  `"code"` group is pinned to `re` (`_FORCE_RE_LANGUAGES`).
  `test/test_fast/test_regex_fast_parity.py` is the guardrail and fails if any
  future pattern diverges.
- **Speed:** ~6.6× faster on the marker workload.

| bench (632 corpus samples) | pure `re` | with `re2` |
|----------------------------|-----------|------------|
| code-only median | 4.18 ms | **1.32 ms** |
| code-only p95 | 103 ms | **17 ms** |
| code-only total | 20.97 s | **3.23 s** |
| cold import | ~73 ms | ~73 ms |

The p95 win matters most: re2 is linear-time, so pathologically large files no
longer blow up.

### 3. The parser trick (opt-in, identifies more languages)

`whats_that_code/parser_detect.py` + `Options(use_parsers=True)`. If code parses
cleanly under a language's grammar, that is strong evidence for it.

- **stdlib validators** (always, no extra): python (`ast`), json, xml
  (`defusedxml`), toml (`tomllib`, 3.11+). New: `parsing_based.parses_as_toml`.
- **tree-sitter grammars** (`[fast]` extra, via `tree-sitter-language-pack`):
  ~26 curated *strict* grammars for languages with no stdlib parser (go, rust,
  ruby, java, kotlin, swift, …).

Two design rules learned the hard way (both encoded in the module):

1. **Clean-parse is permissive.** PHP / HTML / YAML grammars accept almost any
   text; they are excluded. Even among strict grammars the correct language is
   reliably *present* (with a few benign overlaps the clone groups absorb).
1. **Restrict to candidates.** When the election already has candidate languages
   we only test those grammars — a precise disambiguator, not a noisy guesser.
   Parser votes are double-weighted strong evidence and exempt from rare-language
   suppression (a `.zig` that parses as Zig is Zig).

**Measured effect** (Linguist `--limit 20`, test split, seed 0;
`spec/eval_with_parsers.json`):

| Axis | default | `--use-parsers` |
|------|---------|-----------------|
| code only (strict) | 13.0% | **21.5%** (+8.5 pts, +65% rel) |
| with filename (strict) | 48.0% | **53.7%** (+5.6 pts) |

This is the biggest accuracy lever found so far, and it is opt-in, so default
callers are unaffected.

## The `[fast]` extra

`pip install whats_that_code[fast]` → `tree-sitter`, `tree-sitter-language-pack`
(the parser trick's grammars only; `google-re2` is now a core dependency). Without
the extra the parser trick uses only the stdlib validators. The tree-sitter binding
from the language pack is non-standard
(accessors are methods, `parse` takes `str`); `parser_detect` has a capability
probe at import that disables tree-sitter gracefully if the binding misbehaves, so
`use_parsers=True` never crashes — it just falls back to stdlib validators.

## Caveat (unchanged from Phase 2)

Per-language deltas in `--use-parsers` / `--min-tier` aggregate runs are noisy
because `pyrankvote` breaks ties with the unseeded `random` module (phase0
finding #6): the harness seeds `random` once and changing candidate sets upstream
shifts later draws (e.g. the single `haskell` test file flips, yet parses
correctly as haskell in isolation). Trust the aggregate and isolated-file checks.
The recommended deterministic-election fix would remove this noise.

## Future (Phase 4) lever this surfaced

The regex voter is still the dominant cost even with re2. A careful, parity-tested
pruning of redundant/expensive codex patterns (or capping scan length with a
measured no-regression proof) is the next safe speed win. The bench script is the
standing tool for it.
