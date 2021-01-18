# whats_that_code
This is a programming language detection library.

It will detect programming language of source in pure python from an ensemble of classifiers.
Use this when a quick and dirty first approximation is good enough.
whats_that_code can currently identify 60%+ of samples without knowing the extension or tag.

I created this because I wanted
- a pure python programming language detector
- no machine learning dependencies

Tested on python 3.6 through 3.9.

## Usage
```
> code = "def yo():\n   print('hello')"
> guess_language_all_methods(code, file_name="yo.py")
["python"]
```

## How it Works
1) Inspects file extension if available.
2) Inspects shebang
3) Looks for keywords
4) Counts regexes for common patterns
5) Attemps to parse python, json, yaml
6) Inspects tags if available.

Each is imperfect and can error. The classifier then combines the results of each using a voting algorithm

This works best if you only use it for fallback, e.g. classifying code that can't already be classified by extension or tag,
or when tag is ambiguous.

It was a tool that outgrew being a part of [so_pip](https://github.com/matthewdeanmartin/so_pip) a StackOverflow code
extraction tool I wrote.

## Docs
- [TODO](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/TODO.md)
- [LICENSE](https://github.com/matthewdeanmartin/whats_that_code/tree/main/LICENSE)
- [Prior Art](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/prior_art.md) Every similar project/tool, including defunct
- [ChangeLog](https://github.com/matthewdeanmartin/whats_that_code/tree/main/docs/CHANGES.md)

## Notable Similar Tools
- [Guesslang](https://pypi.org/project/guesslang/) - python and tensorflow driven solution. Reasonable results but
slow startup and not pure python.
- [pygments](https://pygments.org/docs/api/#pygments.lexers.guess_lexer) pure python, but sometimes lousy identification
rates.
