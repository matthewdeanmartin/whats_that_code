"""Guess with pygments which can have an accuracy of 10% on SO questions (seems low?)"""

from pygments import lexers
from pygments.lexers import LEXERS

KNOWN_PYGMENTS: dict[str, list[str]] = {}

if not KNOWN_PYGMENTS:

    def init() -> None:
        """Create entries"""
        for key, value in LEXERS.items():
            KNOWN_PYGMENTS[key.replace("Lexer", "").lower()] = list(value[3])

    init()


def language_by_pygments(code: str) -> list[str]:
    """Guess by parsing"""
    if not code or not code.strip():
        return []
    guess = lexers.guess_lexer(code)

    # NOTE: this function used to *mutate* the shared FILE_EXTENSIONS registry here,
    # inserting the pygments lexer name and its extension globs ("learning" new
    # extensions at runtime). That was removed because it made results depend on call
    # history, in two distinct ways:
    #
    #   1. Pygments lexer names are display-cased ("Python"), but FILE_EXTENSIONS keys
    #      are read back as *votes* by extension_based, and the election rejects any
    #      vote that is not lowercase -> `TypeError("Bad casing")` on a later call.
    #   2. Learned entries claim extensions the curated table deliberately assigns
    #      elsewhere. One prolog snippet inserts `cplint` owning `*.pl`, after which
    #      `script.pl` is detected as cplint instead of perl -- a silent accuracy
    #      regression in every subsequent call in the process.
    #
    # Both are order-dependent and invisible in a single-call run. FILE_EXTENSIONS is
    # a curated registry (guarded by test_label_registry.py); it must stay immutable.

    # pygments confuses java & python
    if guess.name.lower().startswith("python"):
        return []
    # pygments confuses gdscript and javascript
    if guess.name.lower().startswith("gdscript"):
        return []
    if "mime" in guess.name.lower():
        return []

    # xml, html, php ...some are subsets of others
    if guess.name.lower() == "xml+php":
        # prefer guessing languages, use xml parser to detect xml
        return ["php"]
    return [guess.name.lower()]
