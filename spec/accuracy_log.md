# Accuracy scoreboard

The running log of measured accuracy changes (spec/spec.md Phase 4). **No accuracy
claim without a number from `scripts/evaluate.py`.** Every row is the test split of
the Linguist corpus, `--limit 20`, recorded with `PYTHONHASHSEED=0`. "strict" =
exact label; code-only is the hard axis, with-filename is the common real call.

Append a row when you change default behavior; never edit history. The current
`spec/eval_baseline.json` is the last "default" row below; `spec/eval_with_parsers.json`
is the last `--use-parsers` row.

| Date | Change | code-only | with-filename | Notes |
|------------|------------------------------------------------------------------|-----------|---------------|---------------------------------------------------|
| 2026-05-31 | **Phase 1 baseline** (nondeterministic; one sample) | 13.0% | 48.0% | random tie-breaks; numbers wobbled run-to-run |
| 2026-05-31 | **Phase 4: deterministic election + crash fixes** | 11.9% | **55.9%** | keystone — see below |
| 2026-05-31 | *(opt-in)* `Options(use_parsers=True)` on the deterministic base | **22.0%** | **61.6%** | Phase 3 parser trick; needs no change to defaults |

## 2026-05-31 — Deterministic election + latent-crash fixes

**What changed (default behavior):**

- The election is now **fully reproducible**: sorted the set-derived vote lists
  (`extension_based`, `tag_based`, `shebang_based`, `guess_by_popularity`) and
  seeded `pyrankvote`'s tie-break via a save/seed(0)/restore of the `random` state
  (doesn't disturb the caller's RNG). Fixes phase0_findings #6.
- `guess_by_popularity` now returns candidates in **popularity order** (most common
  first) instead of set order — deterministic *and* a better ballot ranking.
- Fixed three documented latent crashes (phase0_findings #1, #2): shebangs
  `.awk`/`ash`/`lisp`/`make`/`sed` no longer raise `TypeError` (canonicalized +
  filtered to known labels); the `objective-C` capital-C key (which crashed the
  election's casing check for `.objc` files and `ios`/`iphone` tags) was merged
  into the canonical `objectivec` in `FILE_EXTENSIONS` and `RELATED_TAGS`.

**Measured:** with-filename **+7.9 pts** (48.0→55.9), code-only **−1.1 pts**
(13.0→11.9). The seed-0 tie-break was **chosen on the dev split** (it lands in the
better-performing of two systematic clusters — dev 0.600 vs 0.472 with-filename —
and that choice generalizes to test), not cherry-picked on test.

**Why accept the code-only dip:** with-filename is the common real-world call and
the win there is large and principled (ambiguous extensions like `.h`/`.m`/`.pl`
now resolve toward the popular language). Determinism is itself the headline: a
language detector that returns different answers on re-runs is a latent bug for
every caller. The previously-"unstable" 5/69 characterization entries are now
pinned exactly, so the golden oracle is complete.

**Per-language code-only regressions (deterministic, not noise):** `javascript`
80→20, `java` 100→67 (small n; their tie-breaks now resolve consistently the
"wrong" way on a few files). Tracked for future codex-marker work.

## Error analysis — top code-only failure modes (for future iterations)

From `spec/eval_baseline.json` `top_confusions`. The fallback path (no extension/
tag) over-fires a handful of greedy classifiers:

- **`*→delphi`** (abnf, ampl, javascript, matlab) and **`*→haskell`** (c++, lua,
  ocaml, ruby): the `codex_markers` patterns for delphi/haskell match generic
  operators/symbols. Highest-value target; needs careful per-pattern tightening
  validated against the (now exact) characterization oracle + this scoreboard.
- **`*→python`** (golo, nit, pan): obscure languages with python-like syntax;
  python is correctly common, so suppression won't help — hard cases.
- **`*→ruby`** (clojure, cypher), **`ruby→haskell/python`**: keyword overlap.
- Several `ruby`/`text` "0%" rows are Linguist **filename** samples (`Podfile`,
  `.pryrc`, `Appraisals`) — no extension; whats_that_code does extensions, not
  full-filename matching. Out of scope unless filename matching is added.

**Easiest safe wins not yet taken:** the opt-in parser trick already lifts
code-only to 22% — promoting (some of) it toward the default, behind the
characterization oracle, is the natural next experiment.
