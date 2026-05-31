# How it works

`whats_that_code` is an ensemble classifier. Several independent classifiers each cast votes for one or more candidate languages, and a ranked-choice voting algorithm picks the winner.

## Classifier pipeline

### 1. Extension-based classifier

Extracts the file extension from `file_name` and maps it to the matching language using a built-in extension table. Can also scan `surrounding_text` for words that look like filenames (e.g. `schema.sql`).

**Reliability:** high when a filename is available — gets two votes in the election.

### 2. Shebang-based classifier

Reads the first line of the code. If it starts with `#!`, it maps common interpreter paths to languages.

```
#!/usr/bin/env python  →  python
#!/bin/bash            →  bash
#!/usr/bin/env node    →  javascript
```

**Reliability:** very high when present — gets two votes in the election.

### 3. Tag-based classifier

Maps StackOverflow-style tags to languages. A tag that directly names a language (`python`, `go`) is a strong guess. A tag that names a framework or library (`numpy`, `react`) is a weaker guess. Gets two votes in the election.

### 4. Prior-knowledge classifier

Lets callers supply a list of languages they expect are likely. Validated against the known-language table before voting.

### 5. Regex-feature classifier

Counts structural patterns — regular expressions derived from the [Codex project](https://github.com/TomCrypto/Codex) — that are characteristic of specific languages. Returns candidates ranked by match count.

### 6. Popularity tiebreaker

When the regex and other mid-tier classifiers produce a set of candidates, the popularity classifier re-ranks them by language popularity (based on [PYPL data](https://pypl.github.io/PYPL.html)). This nudges the result toward common languages when the evidence is otherwise ambiguous.

### 7. Keyword-based classifier (fallback)

Counts reserved keywords from a large keyword table covering many languages. Because keywords from one language often appear in another (e.g. `if`, `for`), this classifier is considered a "dumb voter" and is **only consulted when no smarter classifier has voted**.

### 8. Pygments classifier (fallback)

Runs `pygments.lexers.guess_lexer` and maps the result back to the internal language list. Pygments can confuse Python and Java, so its result is filtered and only included when the smarter classifiers abstain.

### 9. Parsing-based validator and classifier

**Always-on validation:** if any classifier voted for `xml`, the code is parsed with
`lxml`. If it does not parse cleanly, the `xml` vote is removed.

**Opt-in parser classifier:** when `Options(use_parsers=True)` is passed, the pipeline
also tries to identify the language by *actually parsing* the code:

- **stdlib validators** (no extra required): Python (`ast`), JSON (`json`), XML (`lxml`),
  and TOML (`tomllib`, Python 3.11+).
- **tree-sitter grammars** (`tree-sitter-language-pack` extra): ~26 curated grammars
  (Go, Rust, C, C++, Java, JavaScript, TypeScript, Ruby, …) that reject unrelated code
  reliably.

A clean parse counts as strong evidence and is double-weighted in the election.
When other classifiers have already proposed candidates, parsing is restricted to those
candidates (precise disambiguation). With no prior candidates it runs across the full
curated grammar set.

## Voting algorithm

The library uses **instant-runoff voting** (IRV) via the `pyrankvote` package. Each classifier produces an ordered list of candidates (most likely first). That list becomes a ranked ballot in the IRV election.

Smart classifiers (extension, shebang, tag) cast two ballots each to reflect their higher reliability. Dumb classifiers (keyword, pygments) are silenced entirely if any smarter classifier has voted, preventing their high false-positive rate from skewing the result.

```
Voters (ballots)
├── Tag classifier          × 2
├── Shebang classifier      × 2
├── Extension classifier    × 2
├── Extension-in-text       × 2
├── Parser classifier       × 2  ← only when Options(use_parsers=True)
├── Prior-knowledge         × 1
├── Regex-feature           × 1
├── Popularity tiebreaker   × 1
├── Keyword classifier      × 1  ← only if all above abstain
└── Pygments classifier     × 1  ← only if all above abstain
```

The IRV winner is returned as the detected language.

## Performance characteristics

- **Speed:** sub-millisecond for short snippets; the regex classifier is the most expensive step.
- **Accuracy:** ~60 %+ on unlabelled snippets; significantly higher when a file extension or tag is available.
- **False positives:** most common for languages with small or overlapping keyword sets (e.g. short SQL vs. HTML fragments).

## Module map

| Module | Role |
|--------|------|
| `election.py` | Orchestrates classifiers and runs the IRV election |
| `extension_based.py` | Extension → language mapping |
| `shebang_based.py` | Shebang line → language mapping |
| `tag_based.py` | Tag → language mapping |
| `keyword_based.py` | Reserved-keyword counting |
| `regex_based.py` | Structural regex feature counting |
| `parsing_based.py` | Python / JSON / XML / TOML parse validation |
| `parser_detect.py` | Opt-in parser classifier (stdlib + tree-sitter grammars) |
| `pygments_based.py` | Pygments lexer wrapper |
| `guess_by_popularity.py` | Popularity-based tiebreaker |
| `known_languages.py` | Master language / extension / popularity tables |
| `languages.py` | Canonical language registry, aliases, and rarity tiers |
| `options.py` | `Options` dataclass for opt-in tuning knobs |
| `codex_markers.py` | Regex patterns (derived from the Codex project) |
| `tags_data.py` | Tag → language relationship data |
| `__main__.py` | CLI entry point |
