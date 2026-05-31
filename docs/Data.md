# Data

## Rebuilding the corpus (Phase 1)

The training/evaluation corpora originally cloned here were lost. They are now
rebuilt on demand by a script — the corpus itself is **gitignored** (size + mixed
per-sample licensing); only the builder, the manifest, and the split are committed.

```bash
make data        # scripts/build_dataset.py --limit 20  → corpus/data/<language>/...
make split       # scripts/split_dataset.py            → corpus/split.json (70/15/15)
make evaluate    # scripts/evaluate.py --split test --baseline spec/eval_baseline.json
```

- **Layout:** `corpus/data/<canonical_language>/<source>__<original_name>`, where the
  language label is normalized to `whats_that_code.languages.CANONICAL`.
- **Source:** GitHub Linguist `samples/` (sparse, shallow, blobless clone — only the
  samples tree is downloaded). Provenance, commit SHA, license, and per-language file
  counts are recorded in `corpus/MANIFEST.json`. Add more sources in
  `scripts/build_dataset.py::SOURCES`.
- **Split:** deterministic and path-hashed (`scripts/split_dataset.py`), so it is
  reproducible and stratified per language. Report accuracy on `test`; tune on `dev`.
- **Reproducibility:** `scripts/evaluate.py` seeds `random` (default `--seed 0`) because
  `pyrankvote` breaks ties with the unseeded `random` module
  (see `spec/phase0_findings.md`). Run with `PYTHONHASHSEED=0` too for full determinism.
- For a larger/thorough corpus, raise the cap: `make data DATA_LIMIT=100` (slower eval).

### Recorded baseline

`spec/eval_baseline.json` (Linguist samples, `--limit 20`, test split, seed 0):

| Axis | strict | lenient |
|------|--------|---------|
| code only | ~13% | ~14% |
| with filename (extension) | ~48% | ~50% |

Code-only detection is weak (the `delphi`/`haskell`/`python` over-firing documented in
`spec/phase0_findings.md`); extension-aware detection is much stronger. These are the
targets for Phase 4. Exact numbers depend on the Linguist commit recorded in
`corpus/MANIFEST.json`.

## Training Sets

- [Rosetta Code](http://www.rosettacode.org/wiki/Rosetta_Code)
- [GuessLangTools](https://github.com/yoeo/guesslangtools) Tool for downloading examples in bulk
- Also see [Prior Art page](prior_art.md), many of those tools posted their training data.

## Input data

- [Reserved Keywords](https://github.com/matthewdeanmartin/Reserved-Key-Words-list-of-various-programming-languages)
- [Languages + Extensions](https://gist.github.com/aymen-mouelhi/82c93fbcd25f091f2c13faa5e0d61760) in JSON form
- [Source Classifier](https://github.com/chrislo/sourceclassifier)

## Aspirational input data (candidate sources for scripts/build_dataset.py)

- [GH Linguist](https://github.com/github-linguist/linguist/tree/main/samples) — **primary source, implemented**
- [Smola](https://github.com/smola/language-dataset/tree/master/data)
- [Rosetta Code](https://github.com/acmeism/RosettaCodeData)
