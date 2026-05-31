"""Characterization (golden) tests — the 'defaults are sacred' tripwire.

These assert that ``guess_language_all_methods`` still produces the outputs it
produced when the corpus was frozen, for the (snippet, axis) combinations that are
deterministic across Python hash seeds. If a later change flips one of these, the
test fails on purpose: either the change is a regression, or it is an intentional
improvement and the contributor re-runs ``python scripts/gen_characterization.py``
and reviews the diff.

The election is hash-seed nondeterministic on its fallback paths (see
spec/phase0_findings.md), so only the seed-stable entries are asserted strictly;
for unstable entries we cannot pin the exact value, so we only require the result
to be a known canonical label (or None).
"""

import json
import os
from pathlib import Path

import pytest

from whats_that_code.election import guess_language_all_methods
from whats_that_code.languages import is_known

CORPUS = Path(__file__).resolve().parent.parent / "data" / "characterization"
EXPECTED_PATH = CORPUS / "expected.json"


def _axis_outputs(code: str, language_dir: str, filename: str) -> dict[str, str | None]:
    # Must mirror scripts/gen_characterization.py::outputs_for
    return {
        "code_only": guess_language_all_methods(code),
        "with_filename": guess_language_all_methods(code, file_name=filename),
        "with_tag": guess_language_all_methods(code, tags=[language_dir]),
    }


def _load_expected() -> dict:
    assert EXPECTED_PATH.exists(), "Run `python scripts/gen_characterization.py` to create expected.json"
    return json.loads(EXPECTED_PATH.read_text(encoding="utf-8"))


def _snippets():
    for path in sorted(CORPUS.rglob("*")):
        if not path.is_file() or path.name == "expected.json":
            continue
        rel = path.relative_to(CORPUS).as_posix()
        language_dir = path.relative_to(CORPUS).parts[0]
        yield rel, language_dir, path.name, path.read_text(encoding="utf-8")


SNIPPETS = list(_snippets())
EXPECTED = _load_expected()


def test_expected_covers_every_snippet():
    """The frozen file must have an entry for every snippet currently on disk."""
    on_disk = {rel for rel, _, _, _ in SNIPPETS}
    frozen = set(EXPECTED["entries"])
    assert (
        on_disk == frozen
    ), f"corpus/expected.json out of sync: only_disk={on_disk - frozen}, only_json={frozen - on_disk}"


@pytest.mark.parametrize("rel,language_dir,filename,code", SNIPPETS, ids=[s[0] for s in SNIPPETS])
def test_characterization(rel, language_dir, filename, code):
    """Stable outputs must match exactly; unstable ones must stay a known label or None."""
    expected = EXPECTED["entries"][rel]
    actual = _axis_outputs(code, language_dir, filename)
    for axis, record in expected.items():
        got = actual[axis]


        if record["stable"]:
            # Can't tell these apart anymore?
            # if got == "html" and record["value"] == "xml" or \
            #     got == "xml" and record["value"] == "html":
            #     continue
            assert got == record["value"], (
                f"{rel} [{axis}] changed: expected {record['value']!r}, got {got!r}. "
                f"If intentional, regenerate with scripts/gen_characterization.py."
            )
        else:
            # Hash-seed dependent (see spec/phase0_findings.md): we cannot pin the exact
            # value, but the election must only ever emit a known canonical label or None.
            # 'observed' lists the values seen at freeze time, for documentation.
            assert got is None or is_known(got), (
                f"{rel} [{axis}] produced {got!r}, which is not a known label nor None. "
                f"Add it to whats_that_code/languages.py if it is a real new label."
            )


def test_some_entries_are_stable():
    """Sanity: the corpus actually exercises deterministic behavior."""
    assert EXPECTED["_meta"]["stable_entries"] > 0


def test_smart_voter_axes_are_mostly_deterministic():
    """Filename/tag-driven results should be far more stable than code-only.

    Documents the design fact that strong evidence (extension/tag) suppresses the
    nondeterministic fallback voters. Guards against a regression that would make
    the smart paths flaky.
    """
    stable = {"with_filename": 0, "with_tag": 0}
    for rec in EXPECTED["entries"].values():
        for axis in stable:
            if rec[axis]["stable"]:
                stable[axis] += 1
    total = len(EXPECTED["entries"])
    assert stable["with_filename"] >= total * 0.7
    assert stable["with_tag"] >= total * 0.7


# Guard against accidentally running with a pinned seed that would mask real
# nondeterminism in the unstable-entry assertions (informational, never fails CI).
def test_report_hash_randomization():
    if os.environ.get("PYTHONHASHSEED") not in (None, "random"):
        pytest.skip(f"PYTHONHASHSEED pinned to {os.environ['PYTHONHASHSEED']}")
