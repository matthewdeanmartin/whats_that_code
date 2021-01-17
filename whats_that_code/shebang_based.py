"""
Guess a language based on shebang
"""

# http://dcjtech.info/topic/list-of-shebang-interpreter-directives/
from typing import List

from whats_that_code.known_languages import FILE_EXTENSIONS

SHEBANGS = {
    "#!/usr/bin/python": "python",
    "#!/usr/bin/env python": "python",
    "#!/usr/bin/env python3": "python",
    "#!/bin/ash": "ash",
    "#!/usr/bin/awk": ".awk",
    "#!/bin/bash": "bash",
    "#!/usr/bin/env bash": "bash",
    "#!/bin/busybox sh": "bash",
    # "#!/bin/csh": ".csh",  # right extension?
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
    # "#!/bin/sh": "bash",
    # "#!/usr/xpg4/bin/sh": ".sh",
    # "#!/bin/tcsh": ".tcsh",
}


def language_by_shebang(test: str) -> List[str]:
    """Identify by shebang"""
    possibles = set()
    for key, value in SHEBANGS.items():
        if key in test:
            possibles.add(value)
        if key.strip("#!/") in test:
            possibles.add(value)

    for possible in possibles:
        if possible not in FILE_EXTENSIONS:
            raise TypeError()
    return list(possibles)
