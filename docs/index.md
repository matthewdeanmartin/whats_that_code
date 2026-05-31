# whats_that_code

`whats_that_code` is a pure-Python programming language detection library. Given a code snippet — with or without a filename, file extension, or tag — it returns the most likely language name.

It is intentionally dependency-light. The only runtime dependencies are `pygments`, `pyrankvote`, and `defusedxml`. There are no machine-learning frameworks to install or model files to download.

## What it does

- identifies the programming language of an arbitrary source-code string
- accepts optional hints: filename, surrounding text, StackOverflow-style tags, or prior probabilities
- combines multiple classifiers through a ranked-choice voting algorithm
- currently identifies 60 %+ of samples without any filename or tag hint
- works as a Python library or a command-line tool

## What it is good for

- classifying code snippets scraped from the web or pasted into forms
- adding language labels to unmarked code blocks in documentation systems
- tagging code extracted from Q&A sites such as StackOverflow
- any situation where you need a best-effort guess and do not want an ML dependency

## What it does not try to be

- a high-accuracy production classifier (consider [Guesslang](https://pypi.org/project/guesslang/) if you need TensorFlow)
- a syntax highlighter or formatter
- a line counter or complexity analyser

## Supported languages

Detection coverage depends on the available hints. The keyword and regex classifiers cover the most common languages. The full language list is in [`known_languages.py`](https://github.com/matthewdeanmartin/whats_that_code/blob/main/whats_that_code/known_languages.py).

## Next steps

- [Installation](installation.md) — install from PyPI or source
- [Usage](usage.md) — Python API and CLI reference
- [How it works](how_it_works.md) — classifier pipeline and voting algorithm
- [Prior art](prior_art.md) — comparable tools and research
- [Changelog](changelog.md)
