"""Guard the canonical language registry against label drift.

Every language label that any data table can emit must be a known label in
``whats_that_code.languages`` (either canonical or a recorded alias). If you add a
new language to a data table and this test fails, add the label to
``languages.CANONICAL`` (or an alias to ``languages.ALIASES``) on purpose — that is
the whole point of the guard. See spec/spec.md Phase 0.
"""

from whats_that_code.codex_markers import MARKERS
from whats_that_code.keyword_based import LANGUAGE_KEY_WORDS
from whats_that_code.known_languages import FILE_EXTENSIONS, POPULARITY_LIST
from whats_that_code.languages import ALIASES, CANONICAL, COMMON, UNCOMMON, canonical, is_known
from whats_that_code.shebang_based import SHEBANGS
from whats_that_code.tags_data import RELATED_TAGS

# Every source of emittable labels in the library. (source name, iterable of labels)
LABEL_SOURCES = {
    "FILE_EXTENSIONS": list(FILE_EXTENSIONS.keys()),
    "POPULARITY_LIST": list(POPULARITY_LIST),
    "LANGUAGE_KEY_WORDS": list(LANGUAGE_KEY_WORDS.keys()),
    "codex_markers.MARKERS": list(MARKERS.keys()),
    "RELATED_TAGS": list(RELATED_TAGS.keys()),
    "shebang_based.SHEBANGS": list(SHEBANGS.values()),
}


def test_every_data_table_label_is_known():
    """No data table may emit a label the registry doesn't know about."""
    unknown: dict[str, list[str]] = {}
    for source, labels in LABEL_SOURCES.items():
        misses = sorted({label for label in labels if not is_known(label)})
        if misses:
            unknown[source] = misses
    assert not unknown, f"Labels not in CANONICAL/ALIASES (add them to languages.py on purpose): {unknown}"


def test_alias_targets_are_canonical():
    """Every alias must point at a real canonical label."""
    bad = {variant: target for variant, target in ALIASES.items() if target not in CANONICAL}
    assert not bad, f"ALIASES pointing at non-canonical targets: {bad}"


def test_alias_keys_are_not_also_canonical():
    """An alias spelling should resolve away, not also live in CANONICAL."""
    overlap = sorted(set(ALIASES) & CANONICAL)
    assert not overlap, f"These spellings are both an alias key and canonical: {overlap}"


def test_canonical_labels_obey_vote_invariants():
    """election.py forbids uppercase and dots in votes; canonical labels must comply.

    (The legacy 'jupyter notebook' label contains a space, which the election
    permits; only uppercase and '.' are rejected there.)
    """
    bad_case = sorted(label for label in CANONICAL if label != label.lower())
    bad_dot = sorted(label for label in CANONICAL if "." in label)
    assert not bad_case, f"Non-lowercase canonical labels: {bad_case}"
    assert not bad_dot, f"Canonical labels containing '.': {bad_dot}"


def test_canonical_is_idempotent():
    """Resolving an already-canonical label returns it unchanged."""
    for label in CANONICAL:
        assert canonical(label) == label


def test_canonical_resolves_known_drift():
    """The drift cases that motivated the registry resolve to one spelling."""
    assert canonical("objective-c") == "objectivec"
    assert canonical("objective-C") == "objectivec"  # the capital-C key bug
    assert canonical("cpp") == "c++"
    assert canonical("make") == "makefile"


def test_tier_sets_are_canonical_labels():
    """Every label in a rarity tier must be a real canonical label (Phase 2)."""
    common_unknown = sorted(COMMON - CANONICAL)
    uncommon_unknown = sorted(UNCOMMON - CANONICAL)
    assert not common_unknown, f"COMMON labels not in CANONICAL: {common_unknown}"
    assert not uncommon_unknown, f"UNCOMMON labels not in CANONICAL: {uncommon_unknown}"


def test_tier_sets_are_disjoint():
    """A label has exactly one tier; it cannot be both common and uncommon."""
    overlap = sorted(COMMON & UNCOMMON)
    assert not overlap, f"Labels in both COMMON and UNCOMMON: {overlap}"
