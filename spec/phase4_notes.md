# Phase 4 notes — the match-rate loop

Recorded 2026-05-31. Phase 4 of `spec/spec.md` is not a one-off change; it is a
**repeatable loop** plus the infrastructure that makes it safe. This note is the
entry point for any future contributor improving accuracy.

## The loop (do this for every accuracy change)

1. **Measure before.** `make evaluate` (or `PYTHONHASHSEED=0 python scripts/evaluate.py
   --limit 20 --baseline spec/eval_baseline.json`). The diff vs the committed
   baseline is your "before".
2. **Hypothesize** from the confusion matrix / worst-languages in the report (and
   the error-analysis section of `spec/accuracy_log.md`).
3. **Change** one thing.
4. **Measure after.** Re-run the harness. A change is acceptable only if the
   aggregate improves (weight with-filename — the common call — heavily) **and**
   there is no unexplained per-language regression.
5. **Guard:** the characterization test (`test/test_fast/test_characterization.py`)
   must stay green, or — if you *intentionally* flip a frozen answer — regenerate
   it with `python scripts/gen_characterization.py` and justify the diff in the PR.
   `make api-check` must stay green.
6. **Record:** append a row to `spec/accuracy_log.md` and, if you changed defaults,
   `make evaluate-baseline` to move the baseline. Never edit scoreboard history.

The standing tools: `scripts/evaluate.py` (accuracy + confusions), `scripts/bench.py`
(`make bench`, latency), the characterization oracle (exact, see below), and
`make api-check` (public surface).

## The keystone: determinism (done 2026-05-31)

Before Phase 4 the election was **not reproducible** — `pyrankvote` broke IRV ties
with the unseeded `random` module and several voters returned `list(set(...))`, so
the same input could yield different answers across runs and across
`PYTHONHASHSEED`. This made step 4 above untrustworthy (you couldn't tell a real
delta from tie-break noise) and is a latent bug for every caller.

Fixed by: sorting every set-derived vote list (`extension_based`, `tag_based`,
`shebang_based`, `guess_by_popularity`) and seeding `pyrankvote`'s tie-break via
`random.getstate()`/`seed(0)`/`setstate()` around the call (deterministic without
disturbing the caller's RNG). `guess_by_popularity` now also orders by popularity,
which is both deterministic and a better ballot ranking.

Result: identical output across runs and hash seeds; the characterization corpus is
now **69/69 axis-entries pinned exactly** (was 52/69), so it is a complete "defaults
are sacred" oracle. The accuracy effect is logged in `spec/accuracy_log.md`
(with-filename +7.9, code-only −1.1, net win). The fixed tie-break seed (0) was
chosen on the **dev** split and generalizes to test — not tuned on test.

### Why not a "principled" popularity tie-break instead of seed 0?
Tried and measured (see git history / prototypes): adding a popularity-ranked
*ballot* over-weights common languages and tanked with-filename to ~0.22; merely
reordering the candidate list passed to `pyrankvote` did **not** make the result
seed-independent (pyrankvote resolves the deciding ties with `random` regardless of
input order). So a fixed seed, chosen on dev, is the pragmatic deterministic
choice. A future option is to replace `pyrankvote`'s final tie resolution with our
own popularity-keyed rule, but that means owning the IRV tie logic.

## Crash fixes shipped this phase (phase0_findings #1, #2)
- Shebangs `.awk`/`ash`/`lisp`/`make`/`sed` used to raise `TypeError`; now
  canonicalized and returned.
- The `objective-C` (capital-C) key crashed the election's casing check for `.objc`
  files and `ios`/`iphone` tags; merged into canonical `objectivec`.

These can only help (crash → answer); negligible corpus-accuracy effect but they
remove real exceptions callers could hit.

## Where to push next (highest value first)
1. **Tighten `codex_markers` for delphi & haskell** — they over-fire on generic
   code and dominate the code-only confusions. Now safe to tune against the exact
   characterization oracle + scoreboard.
2. **Promote part of the parser trick toward the default.** `Options(use_parsers=True)`
   already lifts code-only 11.9%→22.0% and with-filename 55.9%→61.6% on the
   deterministic base. The stdlib validators (no extra needed) are the safest
   candidates to fold into the default clone-group disambiguation.
3. **Clone-group disambiguation via the parsing validators** (extend
   `parsing_based.py`) for c/c++, js/ts, html/xml/php — the spec's original idea.
4. **Replace pyrankvote tie resolution** with a popularity-keyed deterministic rule
   to drop the arbitrary seed and likely recover code-only.
