# Phase 0 findings — label inventory & latent bugs

Recorded 2026-05-31 while building the canonical language registry
(`whats_that_code/languages.py`). None of these are fixed in Phase 0 — fixing them
changes runtime behavior and belongs to a later phase, guarded by the
characterization corpus. They are documented here so the next contributor has the
context.

## Label inventory (the registry snapshot)

`CANONICAL` holds **424** canonical labels, seeded from the union of:

| Source | Distinct keys/values |
|--------|----------------------|
| `known_languages.FILE_EXTENSIONS` | 414 |
| `tags_data.RELATED_TAGS` | 415 |
| `known_languages.POPULARITY_LIST` | 28 |
| `keyword_based.LANGUAGE_KEY_WORDS` | 18 |
| `codex_markers.MARKERS` | 17 (incl. the `code` sentinel) |
| `shebang_based.SHEBANGS` values | 13 |

`ALIASES` records the same-language spelling variants found across those tables:

| Variant | Canonical | Where the variant lives |
|---------|-----------|-------------------------|
| `objective-c` | `objectivec` | `LANGUAGE_KEY_WORDS` |
| `cpp` | `c++` | `codex_markers.MARKERS` (also a `FILE_EXTENSIONS` key) |
| `make` | `makefile` | `MARKERS` + shebang value |
| `.awk` | `awk` | shebang value (malformed) |

## Latent bugs (do NOT fix in Phase 0)

### 1. `objective-C` (capital C) key — can crash the election
`FILE_EXTENSIONS` and `RELATED_TAGS` both contain a key spelled `objective-C`
(capital C). `election.py` validates every vote with
`if vote.lower() != vote: raise TypeError("Bad casing")`. So if the extension or
tag classifier ever emits `objective-C`, the whole call raises `TypeError` instead
of returning a language. `FILE_EXTENSIONS["objective-C"]` therefore points at a set
of extensions whose files are currently un-classifiable (they crash).
**Fix later:** rename the key to `objectivec` (merging with the existing
`objectivec` entry) — strictly an improvement, but it changes behavior, so it needs
the characterization corpus in place first.

### 2. Several shebangs raise `TypeError` instead of returning
`shebang_based.language_by_shebang` ends with
`if possible not in FILE_EXTENSIONS: raise TypeError()`. These shebang values are
**not** keys in `FILE_EXTENSIONS`, so matching their shebang raises:
`.awk`, `ash`, `lisp`, `make`, `sed`. Example: a file starting with
`#!/usr/bin/make -f` crashes rather than returning `makefile`.
**Fix later:** add the missing languages to `FILE_EXTENSIONS` (and fix the `.awk`
value to `awk`), or make the guard skip-and-warn instead of raising.

### 3. `cpp` and `c++` (and `objectivec`) are duplicate languages
`FILE_EXTENSIONS` has both `cpp` and `c++` as separate keys denoting the same
language; `codex_markers` emits `cpp` while keyword/popularity emit `c++`. Both
remain valid emittable labels for backwards compatibility. A future major version
could collapse them via `languages.canonical()`, but that changes emitted spelling
and must be a deliberate, announced change.

### 4. `email` and `code` are not languages
`RELATED_TAGS` has an `email` key (so the tag classifier can "guess" `email` as a
language); `codex_markers` has a `code` sentinel meaning "generic code" (excluded
from the election unless `just_code_is_valid=True`). Kept in `CANONICAL` for
backwards compatibility; flagged as non-language labels.

### 5. `jupyter notebook` contains a space
A legacy `FILE_EXTENSIONS`/`RELATED_TAGS` label. The election only rejects
uppercase and `.` in votes, so a space is tolerated. Left as-is.

### 6. Output is nondeterministic across Python hash seeds
`guess_language_all_methods` is **not** reproducible run-to-run. Several voters
return `list(some_set)` (e.g. `extension_based`, `tag_based`), so the ranked-ballot
order depends on `set` iteration order, which depends on `PYTHONHASHSEED`. When the
result comes down to an IRV tie among fallback candidates, different seeds pick
different winners. Measured on the characterization corpus (23 snippets × 3 axes =
69 cases): **52 stable / 17 unstable** across 8 seeds. The code-only axis is the
worst affected; strong evidence (extension/tag) usually — not always — produces a
single dominant candidate and a stable result.

Examples of seed-dependent answers: `ruby/hello.rb` code-only flips
`ruby`↔`haskell`; `sql/query.sql` with filename flips `sql`↔`delphi`↔`transactsql`;
`perl/script.pl` with filename flips among `perl`/`perl6`/`php`/`prolog`.

**Fix later (recommended, low risk):** sort candidate lists deterministically before
building ballots (e.g. sort the set-derived vote lists, and/or break IRV ties by a
stable key such as popularity then name). This makes results reproducible without
materially changing the intended answer, and would let the characterization test
pin every axis exactly. Until then, the characterization test asserts the 52 stable
cases exactly and only requires the unstable ones to return a known label or `None`.

## Note on Pygments
`pygments_based.language_by_pygments` can emit *any* lowercased Pygments lexer name
and even mutates `FILE_EXTENSIONS` at runtime. The static registry cannot enumerate
that open-ended set; the characterization corpus (frozen outputs) is the practical
guard for Pygments-driven results.
