# Usage

## Python API

### Basic detection

```python
from whats_that_code.election import guess_language_all_methods

language = guess_language_all_methods("print('hello world')")
print(language)  # python
```

The function returns a lower-case language name string, or `None` when the classifier cannot reach a conclusion.

### With a filename hint

Providing the filename lets the extension-based classifier vote with high confidence:

```python
language = guess_language_all_methods(
    code="def greet(name):\n    return f'hello {name}'",
    file_name="greet.py",
)
print(language)  # python
```

### With StackOverflow-style tags

```python
language = guess_language_all_methods(
    code="console.log('hi')",
    tags=["javascript", "node.js"],
)
print(language)  # javascript
```

### With surrounding text

If the code snippet appears inside a larger document that mentions a filename or extension, pass that document text as `surrounding_text`. The classifier scans it for extension clues:

```python
language = guess_language_all_methods(
    code="SELECT * FROM users;",
    surrounding_text="See the file schema.sql for the full definition.",
)
print(language)  # sql
```

### With prior probabilities

When you already have a reasonable guess, pass it as `priors` to give those languages an extra vote:

```python
language = guess_language_all_methods(
    code="package main\nimport \"fmt\"",
    priors=["go", "java"],
)
print(language)  # go
```

### Handling `None`

The function returns `None` when no classifier reaches a conclusion. Always check:

```python
language = guess_language_all_methods(code)
if language is None:
    print("Could not identify language")
else:
    print(f"Detected: {language}")
```

### Function signature

```python
def guess_language_all_methods(
    code: str,
    file_name: str = "",
    surrounding_text: str = "",
    tags: list[str] | None = None,
    priors: list[str] | None = None,
    options: Options | None = None,
) -> str | None:
    ...
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `code` | `str` | Source code string to classify |
| `file_name` | `str` | Filename or path (used for the extension) |
| `surrounding_text` | `str` | Surrounding prose that may contain filename clues |
| `tags` | `list[str]` | Tags from Q&A systems or metadata |
| `priors` | `list[str]` | Language names you expect are likely |
| `options` | `Options` | Optional tuning (see below) |

### Options

`Options` is an opt-in dataclass from `whats_that_code.options` that keeps the public API
stable while allowing new tuning knobs. The default (`None`) reproduces the standard
behavior exactly.

```python
from whats_that_code.options import Options

# Suppress detections of obscure/rare languages unless backed by a file extension,
# shebang, tag, or prior.
language = guess_language_all_methods(code, options=Options(min_tier="common"))

# Also run stdlib + tree-sitter parsers to confirm/identify languages.
language = guess_language_all_methods(code, options=Options(use_parsers=True))
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `min_tier` | `str \| None` | `None` | If `"common"` or `"uncommon"`, suppress rare-language candidates lacking strong evidence |
| `use_parsers` | `bool` | `False` | Run stdlib validators (Python/JSON/XML/TOML) and tree-sitter grammars as an extra classifier |

## Command-line interface

```
whats_that_code [-h] [--version] [--verbose] (-c CODE | -f FILE)
```

### Identify a code string

```bash
whats_that_code -c "print('hello')"
# python
```

### Identify a file

```bash
whats_that_code -f script.py
# python
```

The filename is passed automatically as a hint, so the extension classifier also votes.

### Flags
| `-f FILE`, `--file FILE` | Path to a source file |
| `--verbose` | Enable debug logging |
| `--version` | Print the version and exit |

### Exit codes

| Code | Meaning |
|------|---------|
| `0` | Language detected successfully |
| `1` | Language could not be determined |

### Running as a module

```bash
python -m whats_that_code -c "SELECT 1;"
# sql
```
