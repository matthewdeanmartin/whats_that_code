# whats_that_code

This is a Python programming language detection library.

It detects the programming language of source code with an ensemble of classifiers.
Use this when a quick first approximation is good enough.
Accuracy depends heavily on the available hints; checked-in reports live in `docs/accuracy.md`.

I created this because I wanted

- a Python programming language detector
- no machine learning dependencies

Tested on python 3.10 through 3.14.

## Badges

[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/whats_that_code?longCache=true&style=flat-square)](https://libraries.io/github/matthewdeanmartin/whats_that_code/sourcerank)

[![Downloads](https://static.pepy.tech/badge/whats-that-code/month)](https://pepy.tech/project/whats-that-code)

[![CodeFactor](https://www.codefactor.io/repository/github/matthewdeanmartin/whats_that_code/badge)](https://www.codefactor.io/repository/github/matthewdeanmartin/whats_that_code)

## Usage

```python
from whats_that_code.election import guess_language_all_methods
code = "def yo():\n   print('hello')"
result = guess_language_all_methods(code, file_name="yo.py")
assert result == "python"  # returns a single language name (str), or None if unknown
```

### Suppressing rare languages (opt-in)

Pass an `Options` to avoid guessing obscure languages unless there is strong
evidence (a matching file extension, shebang, or tag). The default is unchanged —
no suppression — so existing callers are unaffected.

```python
from whats_that_code.election import guess_language_all_methods
from whats_that_code.options import Options

# "common" keeps only mainstream languages; "uncommon" also keeps established ones.
guess_language_all_methods(code, options=Options(min_tier="common"))

# A .zig file is still detected as Zig even though Zig is below "common":
guess_language_all_methods(code, file_name="x.zig", options=Options(min_tier="common"))  # -> "zig"
```

### Speed

Regex marker matching (the hottest path) runs on Google's `re2` — a normal
dependency, installed automatically — which is linear-time and ~6× faster on large
inputs, with **identical results**. If a platform has no `re2` wheel it transparently
falls back to stdlib `re`. Nothing to configure.

### The parser trick (optional at runtime)

With `Options(use_parsers=True)` the code is actually parsed; a clean parse is
strong evidence for that language. This uses stdlib parsers (Python/JSON/XML/TOML)
plus ~26 `tree-sitter` grammars that are installed with the main package.

On the evaluation corpus this lifted code-only accuracy from ~13% to ~21% when added. It is off by
default, so existing callers are unaffected.

```python
guess_language_all_methods(go_source, options=Options(use_parsers=True))  # -> "go"
```

## How it Works

1. Inspects file extension if available.
1. Inspects shebang
1. Looks for keywords
1. Counts regexes for common patterns
1. Attempts to parse Python, JSON, XML, and TOML
1. Inspects tags if available.

Each is imperfect and can error. The classifier then combines the results of each using a voting algorithm

This works best if you only use it for fallback, e.g. classifying code that can't already be classified by extension or tag,
or when tag is ambiguous.

It was a tool that outgrew being a part of [so_pip](https://github.com/matthewdeanmartin/so_pip) a StackOverflow code
extraction tool I wrote.

## Docs

- [TODO](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/TODO.md)
- [LICENSE](https://github.com/matthewdeanmartin/whats_that_code/tree/main/LICENSE)
- [Prior Art](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/prior_art.md) Every similar project/tool, including defunct
- [ChangeLog](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/CHANGELOG.md)

## Notable Similar Tools

- [Guesslang](https://pypi.org/project/guesslang/) - python and tensorflow driven solution. Reasonable results but
  slow startup and not pure python.
- [pygments](https://pygments.org/docs/api/#pygments.lexers.guess_lexer) pure python, but sometimes lousy identification
  rates.

## Project Links

- [GitHub](https://github.com/matthewdeanmartin/whats_that_code)
- [PyPI](https://pypi.org/project/whats-that-code/)
- [Bug Tracker](https://github.com/matthewdeanmartin/whats_that_code/issues)
- [Change Log](https://github.com/matthewdeanmartin/whats_that_code/blob/main/CHANGELOG.md)
