"""Corpus accuracy floor (spec/spec.md Phase 1).

Runs the evaluation harness over the rebuilt corpus and asserts accuracy stays
above a recorded floor — a regression guard against changes that tank match rate.

The corpus is gitignored and only present after ``make data`` (build) +
``make split``. When it is absent (e.g. plain CI checkout) the test skips, so it
never blocks check-ci. To run it locally:

    make data        # python scripts/build_dataset.py --limit 20
    make split
    pytest test/test_slow -m slow

Floors are set well below the recorded baseline (see spec/eval_baseline.json) to
absorb the hash-seed nondeterminism of code-only detection (spec/phase0_findings.md)
without flaking.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
CORPUS = REPO / "corpus" / "data"

CODE_ONLY_FLOOR = 0.07
WITH_FILENAME_FLOOR = 0.33


@pytest.mark.slow
def test_corpus_accuracy_floor():
    if not CORPUS.exists() or not any(CORPUS.iterdir()):
        pytest.skip("no corpus on disk — run `make data && make split` to build it")

    sys.path.insert(0, str(REPO / "scripts"))
    import evaluate  # type: ignore[import-not-found]

    which = "test" if (CORPUS.parent / "split.json").exists() else "all"
    report = evaluate.evaluate(CORPUS, which, limit=None)
    overall = report["overall"]

    assert overall["files"] > 0
    assert overall["code_only_strict_accuracy"] >= CODE_ONLY_FLOOR, (
        f"code-only accuracy {overall['code_only_strict_accuracy']:.1%} fell below floor "
        f"{CODE_ONLY_FLOOR:.0%} — likely a regression. Re-run scripts/evaluate.py to inspect."
    )
    assert overall["with_filename_strict_accuracy"] >= WITH_FILENAME_FLOOR, (
        f"with-filename accuracy {overall['with_filename_strict_accuracy']:.1%} fell below floor "
        f"{WITH_FILENAME_FLOOR:.0%} — likely a regression."
    )
