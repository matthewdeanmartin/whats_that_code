"""Guess a language based on shebang"""

# http://dcjtech.info/topic/list-of-shebang-interpreter-directives/
from whats_that_code.languages import canonical, is_known

SHEBANGS = {
    "#!/usr/bin/python": "python",
    "#!/usr/bin/env python": "python",
    "#!/usr/bin/env python3": "python",
    "#!/bin/ash": "ash",
    "#!/usr/bin/awk": ".awk",
    "#!/bin/bash": "bash",
    "#!/usr/bin/env bash": "bash",
    "#!/bin/busybox sh": "bash",
    "#!/usr/local/bin/groovy": "groovy",
    "#!/usr/bin/env groovy": "groovy",
    "#!/usr/bin/env jsc": "javascript",
    "#!/usr/bin/env node": "javascript",
    "#!/usr/bin/env rhino": "javascript",
    "#!/usr/local/bin/sbcl --script": "lisp",
    "#!/usr/bin/env lua": "lua",
    "#!/usr/bin/lua": "lua",
    "#!/usr/bin/make -f": "make",
    "#!/usr/bin/env perl": "perl",
    "#!/usr/bin/perl": "perl",
    "#!/usr/bin/perl -T": "perl",
    "#!/usr/bin/php": "php",
    "#!/usr/bin/env php": "php",
    "#!/usr/bin/env ruby": "ruby",
    "#!/usr/bin/ruby": "ruby",
    "#!/bin/sed -f": "sed",
    "#!/usr/bin/sed -f": "sed",
    "#!/usr/bin/env sed": "sed",
}


def language_by_shebang(test: str) -> list[str]:
    """Identify by shebang.

    Shebang values are canonicalized (e.g. the malformed ``.awk`` -> ``awk``,
    ``make`` -> ``makefile``) and filtered to known labels. Previously any value
    not present as a ``FILE_EXTENSIONS`` key (``.awk``/``ash``/``lisp``/``make``/
    ``sed``) raised ``TypeError`` — a latent crash (spec/phase0_findings.md #2).
    Sorted output keeps the election deterministic (spec/phase4_notes.md).
    """
    possibles: set[str] = set()
    for key, value in SHEBANGS.items():
        if key in test:
            possibles.add(value)
        if key.strip("#!/") in test:
            possibles.add(value)

    return sorted({canonical(possible) for possible in possibles if is_known(possible)})
