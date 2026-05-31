# Installation

## Requirements

- Python 3.10 or newer
- No C extensions, ML frameworks, or model downloads required

## Install from PyPI

```bash
pip install whats_that_code
```

## Recommended: `pipx` (for CLI use)

If you mainly want the command-line tool rather than the library, `pipx` installs it into an isolated environment:

```bash
pipx install whats_that_code
```

## From source

```bash
git clone https://github.com/matthewdeanmartin/whats_that_code.git
cd whats_that_code
uv sync --all-extras
```

## Verifying the install

```bash
whats_that_code --version
```

Or as a module:

```bash
python -m whats_that_code --version
```

## Runtime dependencies

| Package | Purpose |
|---------|---------|
| `pygments` | Fallback lexer-based classifier |
| `pyrankvote` | Instant-runoff voting for the ensemble |
| `defusedxml` | Safe XML parsing for XML/HTML detection |

These are installed automatically with `pip install whats_that_code`.
