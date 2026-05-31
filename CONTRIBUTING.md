# Contributing

Thanks for contributing to `whats_that_code`.

This project uses `uv` for Python tooling and a Makefile for common workflows. CI follows the same toolchain, so the safest local setup is to use the same commands.

## Setup

```bash
git clone https://github.com/matthewdeanmartin/whats_that_code.git
cd whats_that_code
uv sync --all-extras
```

List available project commands:

```bash
uv run make help
```

## Common local commands

Run the full local quality gate:

```bash
uv run make check
```

Run the CI-style quality gate:

```bash
uv run make check-ci
```

Run individual checks:

```bash
uv run make lint
uv run make typecheck
uv run make test
uv run make security
uv run make docs-check
uv run make build-docs
uv run make tox
```

Useful supporting commands:

```bash
uv run make format
uv run make format-check
uv run make spell
```

## What CI runs

The GitHub Actions workflow installs dependencies with:

```bash
uv sync --all-extras
```

Then runs:

```bash
uv run make check-ci
```

A separate `tox` workflow runs `tox -e py` across Python 3.10–3.13 on Ubuntu and Windows.

## Adding a new language

1. Add the language name and its file extensions to `known_languages.py` (`FILE_EXTENSIONS` dict).
1. Add a popularity rank entry to `POPULARITY` if the language is commonly known.
1. Add regex feature markers to `codex_markers.py` (`MARKERS` dict) if distinctive patterns exist.
1. Add keyword lists to `keyword_based.py` (`LANGUAGE_KEY_WORDS` dict).
1. Add shebang entries to `shebang_based.py` (`SHEBANGS` dict) if the language has a standard shebang.
1. Add tag relationships to `tags_data.py` (`RELATED_TAGS` dict) if the language has well-known ecosystem tags.
1. Add or update tests in `test/`.

## Running tests

```bash
uv run pytest
```

Target a single file:

```bash
uv run pytest test/test_election.py
```

## Submitting changes

1. Fork the repository.
1. Create a branch named `feature/your-change` or `fix/your-fix`.
1. Write or update tests to cover your change.
1. Run `uv run make check-ci` and confirm it passes.
1. Open a pull request against `main`.

## Code style

- Formatted with `black` (line length 120).
- Imports sorted with `isort`.
- Type-annotated throughout; `mypy` is run in CI.
- Docstrings follow Google style.
