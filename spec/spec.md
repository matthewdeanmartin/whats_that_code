# whats_that_code — Modernization & Improvement Plan

**Status:** Draft for execution
**Author:** (planning session, 2026-05-30)
**Audience:** Any single contributor picking up one phase. Each phase is written to be
self-contained — you should not need to have done the previous phase yourself, only to
trust that its *deliverables* exist. Read **§1–§3** once, then jump to your phase.

______________________________________________________________________

## 1. Why this document exists

`whats_that_code` is a pure-Python, no-ML programming-language detector. It is an ensemble
("election") of independent classifiers whose votes are combined by instant-runoff voting.
It ships ~2,000 downloads/month and is depended on by at least the author's `so_pip` tool.

Four things need to happen, roughly in priority order:

1. **Re-establish the training/evaluation dataset.** The corpora originally cloned (see
   `docs/Data.md`) are no longer on disk. The slow test `test/test_slow/test_classify_all.py`
   silently `pytest.skip`s because `examples/sourceclassifier-master/sources` is gone, so we
   are currently flying blind on accuracy.
1. **Modernize the label system.** Keep every existing label working (backwards compatible),
   but allow many more, contemporary languages — *and* give callers a way to say "don't match
   on rare languages."
1. **Improve performance.** It has never been profiled; the suspicion is that it is slow.
   Optional native-library acceleration may help.
1. **Systematically improve match rates** with a repeatable measure-change-measure loop.

**Overriding constraint: backwards compatibility.** 2,000 downloads/month means we must not
break callers. Improvements must be *API-conservative*. New behavior is opt-in; defaults
reproduce today's results. See §3.

______________________________________________________________________

## 2. Current architecture (the 5-minute orientation)

Public entry points (these are the API contract — treat as frozen, see §3):

| Symbol | Signature | Returns |
|--------|-----------|---------|
| `whats_that_code.election.guess_language_all_methods` | `(code, file_name="", surrounding_text="", tags=None, priors=None)` | `str \| None` |
| `whats_that_code.guess_by_code_and_tags.assign_extension` | `(all_code, tags)` | `tuple[str, str]` (extension, language) |
| `python -m whats_that_code` (CLI) | `-c CODE \| -f FILE [--verbose] [--version]` | prints language or `Unknown` |

The election (`election.py`) gathers votes from these classifiers:

| Module | Method | Tier | Notes |
|--------|--------|------|-------|
| `extension_based.py` | filename / in-text extension → language | smart (×2 votes) | uses `FILE_EXTENSIONS` |
| `shebang_based.py` | `#!` line → language | smart (×2) | |
| `tag_based.py` | SO tag → language | smart (×2) | uses `tags_data.RELATED_TAGS` |
| `election.guess_by_prior_knowledge` | caller-supplied likely langs | mid | validated vs `FILE_EXTENSIONS` |
| `regex_based.py` | structural regex features | mid | uses `codex_markers.MARKERS` (~17 langs incl. `"code"`) |
| `guess_by_popularity.py` | re-rank candidates by PYPL rank | mid | uses `POPULARITY_LIST` (28 langs) |
| `keyword_based.py` | reserved-keyword counting | dumb (fallback only) | ~20 langs, large hand table |
| `pygments_based.py` | `pygments.guess_lexer` | dumb (fallback only) | filtered (py/java confusion etc.) |
| `parsing_based.py` | `ast` / `json` / `defusedxml` validation | validator | currently only used to veto `xml` |

Data tables (the things that define "what languages exist"):

- `known_languages.py` — `FILE_EXTENSIONS` (~440 keys), `POPULARITY` / `POPULARITY_LIST` (28),
  `CLONES` (`xml/html/php`, `c/c++`, `javascript/typescript`).
- `tags_data.py` — `RELATED_TAGS` (~12k lines).
- `codex_markers.py` — compiled regex markers per language.
- `keyword_based.py` — `LANGUAGE_KEY_WORDS`.

Dependencies are deliberately tiny: `pyrankvote`, `defusedxml`, `pygments`. The project's
selling point is "pure python, no ML." Preserve that posture; any heavy/native dependency
must be an **optional extra**, never a hard requirement.

______________________________________________________________________

## 3. Guiding principles & guardrails (read before touching anything)

1. **The public API in §2 is frozen.** `guess_language_all_methods` must keep returning
   `str | None` with the same parameters. New options are added only as **new keyword
   arguments with defaults that reproduce current behavior**, or as new functions/objects.
   No positional reordering, no renames, no return-type changes.
   - ⚠️ Known doc bug: `README.md` shows `result == ["python"]` (a list) but the function
     returns a `str`. The *code* is the contract; fix the docs, not the behavior (Phase 0).
1. **Labels are forever.** Any label a caller can receive today (every key of
   `FILE_EXTENSIONS`, plus `POPULARITY`, plus whatever `pygments` can emit) must continue to
   be a possible return value, spelled the same way. New labels are additive.
1. **Defaults are sacred.** Calling with the old signature must produce the *same answer* it
   does today for the characterization corpus (Phase 0). Behavior changes ride behind opt-in
   flags until a deliberate major-version bump.
1. **Pure-Python by default.** Native acceleration is an extra (`pip install whats_that_code[fast]`) with a pure-Python fallback that is always present.
1. **Measure before and after.** No accuracy or perf change lands without a number from the
   harness (Phase 1) showing it did not regress.

### 3a. Recommended API / schema validation (the user asked for a suggestion)

The codebase already hand-rolls invariant checks in `election.py` (votes must be lowercase,
must not contain `.`, else `raise TypeError`). That instinct is right but under-built. Concrete,
low-dependency recommendations, in order of value:

- **A canonical language registry + data-table validation (highest value, do in Phase 0).**
  Today the same language is spelled differently across tables — e.g. `POPULARITY` has
  `"objectivec"` while `keyword_based` has `"objective-c"`; SQL dialects (`mariadb`,
  `postgresql`, `sqlite`, `transact-sql`, `oracle`) appear in keywords but may not line up
  with `FILE_EXTENSIONS` keys. There is no single source of truth for "valid label." Create
  one (`languages.py`: a frozenset/registry of canonical names + an alias map), then add a
  test that asserts **every key of every data table is either a canonical name or a known
  alias.** This is the single most important safety net for "backwards compatible labels" and
  it needs no new dependency.
- **Public-API surface snapshot.** `griffe` is *already* a dev dependency. Add a test/CI step
  that dumps the public API of `whats_that_code` and diffs it against a checked-in snapshot, so
  any signature/label-shape change is a deliberate, reviewed event rather than an accident.
- **Characterization ("golden") tests.** Freeze current outputs for a fixed snippet corpus
  (see Phase 0) and assert they don't change unless intended. This is how you keep defaults
  sacred while refactoring internals.
- **A typed options object for new knobs.** When Phase 2/4 add options (rare-language
  suppression, allow-lists), prefer a single `@dataclass(frozen=True)` `Options`/`Config`
  passed as one optional kwarg rather than growing the positional signature. Validate it in
  `__post_init__`. Avoid adding `pydantic` — a stdlib dataclass keeps the "no heavy deps"
  promise. Use `jsonschema` (dev-only) if/when data tables move to JSON/YAML files.

______________________________________________________________________

## 4. Phases

> Each phase below lists: **Goal · Context you need · Tasks · Deliverables · Acceptance
> criteria · Backwards-compat guardrails · Handoff.** Phases 0→4 are ordered, but only
> Phase 0 is a hard prerequisite for the rest. Phase 0 *must* be done first.

______________________________________________________________________

### Phase 0 — Safety net & ground truth (do this first)

**Goal:** Make it impossible to silently break the API, the labels, or the default behavior.
Nothing here changes runtime behavior; it only adds tests, a registry, and docs fixes.

**Context you need:** §2 and §3. That's it.

**Tasks**

1. **Canonical language registry.** Create `whats_that_code/languages.py` with:
   - `CANONICAL: frozenset[str]` — every language label the library can emit today. Seed it by
     unioning the keys of `FILE_EXTENSIONS`, `POPULARITY_LIST`, `LANGUAGE_KEY_WORDS`,
     `codex_markers.MARKERS`, and `RELATED_TAGS`.
   - `ALIASES: dict[str, str]` — map variant spellings to canonical (e.g.
     `"objective-c" -> "objectivec"`, or vice-versa; pick whichever spelling the *public
     return value* uses today and make the other an alias — **do not change emitted spelling**).
   - A `canonical(name) -> str` helper. Do **not** wire it into the election yet; this phase is
     inventory + tests only.
1. **Data-consistency test.** `test/test_fast/test_label_registry.py`: assert every key in
   every data table is in `CANONICAL` or `ALIASES`. Expect this to FAIL initially — that
   failure is the inventory of label drift. Resolve by adding aliases (not by renaming public
   labels). Document each mismatch found.
1. **Characterization corpus + golden test.** Assemble ~50–100 short, license-clean snippets
   (you can write them yourself or borrow tiny ones) spanning the common languages. Store as
   `test/data/characterization/<lang>/<n>.txt` plus an expected-output JSON. Add
   `test/test_fast/test_characterization.py` that runs `guess_language_all_methods` and asserts
   the *current* output. This is the "defaults are sacred" tripwire for every later phase.
   - Capture outputs across the full input matrix: code-only, code+filename, code+tags.
1. **Public-API snapshot.** Add a `make api-snapshot` target using `griffe` (already a dev dep)
   that writes `spec/api_surface.json`, and a `make api-check` that diffs current vs snapshot
   and fails on change. Wire `api-check` into CI (`make check-ci`).
1. **Fix the README example** (`result == ["python"]` → `result == "python"`) and any doc that
   implies a list return. Behavior unchanged.

**Deliverables:** `languages.py`, three new tests, `api_surface.json`, Make targets, README fix.

**Acceptance criteria:** `make check-ci` green; label-registry test green (after aliases added);
characterization test green; api-check green and wired into CI.

**Backwards-compat guardrails:** This phase *defines* the guardrails. The only public change is
a docs fix.

**Handoff:** Later phases assume `languages.CANONICAL`/`ALIASES`, the characterization corpus,
and `api-check` all exist. They are the regression oracle for everything else.

______________________________________________________________________

### Phase 1 — Re-establish the dataset

**Goal:** A reproducible, license-aware pipeline that rebuilds the training/evaluation corpora
so accuracy is measurable again, plus a standing **evaluation harness** that prints match rate.

**Context you need:** `docs/Data.md`, `docs/prior_art.md`, `test/test_slow/test_classify_all.py`
(shows the historical corpus layout: `examples/sourceclassifier-master/sources`, files named by
extension), and Phase 0's characterization corpus (different thing — that one is tiny & frozen;
this one is large & for scoring).

**Known sources (verify availability; some moved):**

- Rosetta Code dataset — `github.com/acmeism/RosettaCodeData` (large, per-language dirs).
- GitHub Linguist samples — `github.com/github-linguist/linguist/tree/main/samples`.
- `smola/language-dataset`.
- `chrislo/sourceclassifier` (the original `sources/` dir the old test expected).
- GuessLangTools — bulk downloader for examples.
  Each has its own license; record provenance and license per source.

**Tasks**

1. **`make data` / `scripts/build_dataset.py`:** download (or git-clone shallow) the chosen
   sources into a gitignored `examples/` (or `corpus/`) tree, normalized to
   `corpus/<canonical_lang>/<id>.<ext>`. Map source-specific language names → `languages.CANONICAL`.
   Do **not** commit the corpus (size/license); commit the *builder* and a manifest.
1. **Manifest & licensing:** `corpus/MANIFEST.json` recording source, URL, commit/snapshot date,
   license, and file count per language. Update `docs/Data.md` to describe the rebuild process
   and dead links.
1. **Held-out split:** deterministic train/dev/test split (seeded) so accuracy numbers are
   stable and not contaminated by tuning.
1. **Evaluation harness `scripts/evaluate.py` (the core deliverable):** runs
   `guess_language_all_methods` over the dev/test split and reports overall accuracy, a
   per-language confusion matrix, and top mispredictions. Output both human-readable and a
   machine-readable `eval_report.json`. Support a `--baseline` flag to diff against a saved run.
1. **Revive the slow test:** rewrite `test/test_slow/test_classify_all.py` to consume the new
   corpus layout (still `pytest.skip` if corpus absent, so CI without the corpus stays green),
   and assert accuracy stays above a recorded floor.
1. **Record the baseline number** in `spec/spec.md` or `eval_report.json` so Phases 2–4 have a
   "before."

**Deliverables:** dataset builder, manifest, eval harness, revived slow test, recorded baseline
accuracy (overall + per-language).

**Acceptance criteria:** A contributor can run `make data && python scripts/evaluate.py` and get
a reproducible accuracy report. Baseline committed. CI unaffected when corpus absent.

**Backwards-compat guardrails:** Read-only — this phase does not touch the classifier or labels.

**Handoff:** Phases 2 & 4 *require* `scripts/evaluate.py` and the recorded baseline. No accuracy
claim is valid without an eval-harness number.

______________________________________________________________________

### Phase 2 — Label modernization (backwards-compatible + new + rare-suppression)

**Goal:** Support many more contemporary languages, keep every old label, and add an opt-in way
to suppress rare-language matches.

**Context you need:** Phase 0 (`languages.py`, characterization test, api-check) and Phase 1
(eval harness) must exist. §3 guardrails are binding here especially.

**Tasks**

1. **Promote `languages.py` to the source of truth.** Give each language a record: canonical
   name, aliases, file extensions, optional shebang interpreters, optional SO tags, and a
   **rarity/popularity tier** (e.g. `common` / `uncommon` / `rare`, derived from PYPL +
   GitHub/Linguist frequency). Existing tables (`FILE_EXTENSIONS`, `POPULARITY`, etc.) become
   *views* derived from this registry, or are validated against it. Migrate incrementally — keep
   old tables working until the registry fully backs them.
1. **Add new languages additively.** Expand the registry with modern languages (e.g. typescript
   variants, kotlin, rust, dart, zig, nim, julia, etc. — many already partly present). Each new
   language ships with at least extension + tag data; regex/keyword markers optional.
1. **Rare-language suppression (the requested feature).** Add an opt-in knob. Recommended shape
   (per §3a, a typed options object so the signature stays stable):
   ```python
   guess_language_all_methods(code, ..., options=Options(min_tier="common"))
   # or a thin convenience kwarg that builds Options internally
   ```
   When set, the election excludes (or heavily down-weights) candidates below the tier *unless*
   strong evidence exists (a matching extension/shebang/tag should still win — a `.zig` file is
   Zig even if Zig is "rare"). **Default = no suppression**, i.e. today's behavior exactly.
1. **Confidence signal (optional but recommended).** Consider a sibling function that returns
   ranked candidates with scores (e.g. `guess_language_ranked(...) -> list[tuple[str, float]]`)
   so callers can implement their own rarity policy. Additive, does not touch the existing
   function.

**Deliverables:** registry-backed `languages.py`, new languages, `Options` dataclass with
rarity suppression, optional ranked-result function, tests.

**Acceptance criteria:**

- Characterization test (Phase 0) still green → defaults unchanged.
- New test: every old label still emittable; new labels emittable when evidence present.
- New test: with `min_tier="common"`, rare languages are suppressed *except* under strong
  extension/shebang/tag evidence.
- Eval harness (Phase 1): overall accuracy on common languages does not regress; coverage of new
  languages measurable.
- `api-check`: any new public symbol/kwarg is a reviewed, intentional snapshot update.

**Backwards-compat guardrails:** New behavior strictly opt-in. No emitted label changes spelling.
No positional-arg changes. If a registry migration would change an emitted label's spelling, add
an alias and keep emitting the old spelling.

**Handoff:** Phase 4 tunes the rarity tiers and weights using the eval harness.

______________________________________________________________________

### Phase 3 — Performance

**Goal:** Make it measurably faster without changing results or the pure-Python default.

**Context you need:** Phase 0 characterization test (your "results unchanged" oracle) and Phase 1
eval harness (your "accuracy unchanged" oracle). You do **not** need Phase 2.

**Suspected hot spots (confirm by profiling, don't assume):**

- `pygments.guess_lexer` — typically the most expensive single call.
- `regex_based.language_by_regex_features` — iterates all markers × all patterns over the text.
- `keyword_based.guess_by_keywords` — nested loop over words × languages.
- Module-import cost (large `tags_data.py`, building `KNOWN_PYGMENTS` at import).

**Tasks**

1. **Profile first.** Add `scripts/profile.py` (cProfile + a representative snippet mix from the
   Phase 1 corpus). Produce a before-number: median + p95 latency per snippet, and import time.
   Record it. **No optimization is accepted without this baseline.**
1. **Pure-Python wins (no new deps):** precompile/curry regexes once at import; short-circuit
   classifiers when a high-confidence smart vote already exists; lazy-import `pygments` and skip
   it entirely when smart voters have spoken (the election already silences it — make it not even
   *run*); consider lazy/segmented loading of `tags_data`.
1. **Optional native acceleration (extra, never required):** e.g. fast keyword scanning via
   `pyahocorasick`, or `google-re2`/`regex` for marker matching, behind
   `whats_that_code[fast]` with a pure-Python fallback. If `tree-sitter` is explored for real
   parse-based validation, it is strictly an extra and an additive validator — never a hard dep.
1. **Micro-benchmark in CI (advisory):** keep `scripts/profile.py` runnable; optionally a
   `make bench` target. Don't gate CI on wall-clock (flaky), but record numbers in PRs.

**Deliverables:** profiler script + recorded before/after numbers, the optimizations, optional
`[fast]` extra with fallback, docs note on the extra.

**Acceptance criteria:** Characterization + eval outputs **identical** before/after (perf must not
change answers — if native libs differ, the fallback path is the source of truth and any
native-path divergence is a bug). Measurable latency/import improvement with numbers in the PR.

**Backwards-compat guardrails:** Same answers, same labels, same public API. Native libs optional
with guaranteed pure-Python fallback so existing installs are unaffected.

**Handoff:** None required; independent of other phases.

______________________________________________________________________

### Phase 4 — Systematic match-rate improvement

**Goal:** A repeatable measure → hypothesize → change → measure loop that raises accuracy
without regressing any language or breaking defaults.

**Context you need:** Phase 1 eval harness + baseline (required). Phase 0 oracles. Phase 2
registry helps but is not strictly required.

**Tasks**

1. **Error analysis loop:** use `scripts/evaluate.py` confusion matrix to find the worst
   language pairs (likely SQL-dialect collisions, c/c++/objectivec, html/xml/php,
   js/ts, python/coffeescript, etc.). Document the top failure modes.
1. **Targeted, low-risk improvements**, each validated by the harness, e.g.:
   - Tune election vote weights / the "smart vs dumb voter" gating (currently hand-set ×2).
   - Better clone disambiguation (`CLONES`): use the parsing validators (`ast`, `json`, xml,
     and possibly add TS/JS, c/c++ heuristics) to break ties — extend `parsing_based.py` rather
     than the dumb voters.
   - Improve shebang coverage and tag→language mappings (cheap, high precision).
   - Expand/clean `codex_markers` for high-confusion languages.
1. **Guard every change** with: characterization test green (defaults sacred), eval harness
   shows overall ↑ and **no per-language regression beyond a small tolerance**, api-check green.
1. **Track a scoreboard:** append each experiment's eval delta to a log
   (`spec/accuracy_log.md`) so progress is visible and regressions are attributable.
1. **Consider a "is this even code?" gate** (the old Release 3.0 TODO) only as an additive,
   opt-in classifier — out of scope for default behavior.

**Deliverables:** error-analysis notes, a series of small validated improvements, accuracy
scoreboard, updated baseline.

**Acceptance criteria:** Net overall accuracy improvement vs Phase 1 baseline with no
unexplained per-language regression; all Phase 0 oracles green; every change has a recorded
before/after number.

**Backwards-compat guardrails:** Accuracy changes *will* shift some individual answers — that is
expected and allowed for the **default** path *only when the aggregate improves and the change is
reviewed*. The characterization corpus should be updated deliberately (with justification in the
PR) when a change intentionally flips a previously-frozen answer; never edit it casually to make a
test pass. Public API and label spellings remain frozen.

**Handoff:** Ongoing; the loop is the deliverable.

______________________________________________________________________

## 5. Suggested sequencing & ownership

| Order | Phase | Hard prereq | Can run in parallel with |
|-------|-------|-------------|--------------------------|
| 1 | Phase 0 (safety net) | none | — (must finish first) |
| 2 | Phase 1 (dataset) | Phase 0 | Phase 3 |
| 3 | Phase 3 (perf) | Phase 0 | Phase 1 |
| 4 | Phase 2 (labels) | Phase 0, Phase 1 | — |
| 5 | Phase 4 (match rate) | Phase 1 | — |

Phase 0 is the gate. After it, perf (3) and dataset (1) can proceed independently. Labels (2)
and match-rate (4) both depend on the eval harness from Phase 1.

## 6. Definition of done for the whole effort

- Reproducible dataset builder + standing eval harness with a recorded, improvable baseline.
- Single canonical language registry; all data tables validated against it; old labels frozen,
  many new labels supported; opt-in rare-language suppression.
- Profiled, measurably faster, with optional native acceleration and a pure-Python fallback.
- A working measure-change-measure accuracy loop with a visible scoreboard.
- Public API unchanged for existing callers; api-check + characterization tests guarding it in CI.
