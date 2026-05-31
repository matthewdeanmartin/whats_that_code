"""Guess with pygments which can have an accuracy of 10% on SO questions (seems low?)"""

from pygments import lexers
from pygments.lexers import LEXERS

from whats_that_code.known_languages import FILE_EXTENSIONS

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

    if guess.name not in FILE_EXTENSIONS:
        lexer_name = str(guess.language_lexer.name if hasattr(guess, "language_lexer") else guess.name).lower()
        if lexer_name in KNOWN_PYGMENTS:
            FILE_EXTENSIONS[guess.name] = KNOWN_PYGMENTS[lexer_name]

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
