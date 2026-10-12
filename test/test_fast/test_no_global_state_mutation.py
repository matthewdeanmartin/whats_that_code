"""Detection must not depend on what was detected before it.

``pygments_based.language_by_pygments`` used to "learn" new entries into the shared
``known_languages.FILE_EXTENSIONS`` registry at runtime. Because that registry's keys
are read back as *votes* by ``extension_based``, one earlier call could change (or
crash) every later call in the same process:

* pygments lexer names are display-cased ("Python"), and the election rejects any
  vote that is not lowercase -> ``TypeError("Bad casing")``;
* a learned entry can claim an extension the curated table assigns elsewhere --
  a prolog snippet teaches ``cplint`` to own ``*.pl``, after which ``script.pl``
  detects as cplint instead of perl.

Both failures are order-dependent, so they only appear once some other call has run
first (which is why they surfaced under randomized test ordering, not in isolation).
These tests pin the invariant directly.
"""

from __future__ import annotations

import copy

from whats_that_code.election import guess_language_all_methods
from whats_that_code.known_languages import FILE_EXTENSIONS
from whats_that_code.pygments_based import language_by_pygments

PERL = (
    'use strict;\nuse warnings;\n\nmy @nums = (1, 2, 3);\nmy $total = 0;\n$total += $_ for @nums;\nprint "$total\\n";\n'
)
PROLOG = "main :- write(hello), nl.\n"

# Snippets chosen to make pygments reach for a variety of exotic lexers.
SNIPPETS = [
    PROLOG,
    PERL,
    "def f(x):\n    return x + 1\n",
    '{"a": [1, 2, 3]}',
    'package main\nimport "fmt"\nfunc main() { fmt.Println(1) }\n',
    "SELECT id, name FROM users WHERE id = 1;\n",
    '<?xml version="1.0"?><root><child/></root>',
]


def test_pygments_does_not_mutate_the_extension_registry():
    """language_by_pygments must leave FILE_EXTENSIONS exactly as it found it."""
    before = copy.deepcopy(FILE_EXTENSIONS)
    for snippet in SNIPPETS:
        language_by_pygments(snippet)
    assert before == FILE_EXTENSIONS, "language_by_pygments mutated the shared FILE_EXTENSIONS registry"


def test_registry_keys_stay_lowercase():
    """Every FILE_EXTENSIONS key must be a legal vote (the election rejects casing)."""
    for snippet in SNIPPETS:
        language_by_pygments(snippet)
    bad = [key for key in FILE_EXTENSIONS if key != key.lower()]
    # "objective-C" is a known, pre-existing exception recorded in spec/phase0_findings.md.
    assert [k for k in bad if k != "objective-C"] == []


def test_detection_is_independent_of_call_history():
    """A prolog snippet must not change how a later perl file is detected."""
    baseline = guess_language_all_methods(PERL, file_name="script.pl")
    for snippet in SNIPPETS:
        guess_language_all_methods(snippet)
    assert guess_language_all_methods(PERL, file_name="script.pl") == baseline
