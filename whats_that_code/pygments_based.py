"""
Guess with pygments which can have an accuracy of 10% on SO questions (seems low?)
"""
from typing import List

from pygments import lexers
from pygments.lexers import LEXERS

from whats_that_code.known_languages import FILE_EXTENSIONS

KNOWN_PYGMENTS = {}

if not KNOWN_PYGMENTS:

    def init():
        """Create entries"""
        for key, value in LEXERS.items():
            # print(f' "{key.replace("Lexer","").lower()}", {list(value[3])},')
            KNOWN_PYGMENTS[key.replace("Lexer", "").lower()] = list(value[3])

    init()


def language_by_pygments(code: str) -> List[str]:
    """Guess by parsing"""
    if not code or not code.strip():
        return []
    guess = lexers.guess_lexer(code)

    if guess.name not in FILE_EXTENSIONS:
        if hasattr(guess, "language_lexer"):
            lexer_name = guess.language_lexer.name
        else:
            lexer_name = guess.name
        lexer_name = str(lexer_name).lower()
        if lexer_name in KNOWN_PYGMENTS:
            FILE_EXTENSIONS[guess.name] = KNOWN_PYGMENTS[lexer_name]
        else:
            pass
            # print("What pygment thing is this: " + lexer_name)

    # pygments confuses java & python
    if guess.name.lower().startswith("python"):
        return []  # ["python"]
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
