# whats_that_code
This is a programming langauge detection library.

It will detect programming language of source in pure python from an ensemble of classifiers

It aims to detect languages when a quick and dirty first approximation is good enough.
whats_that_code can currently identify 60%+ of files without knowing the extension or tag.

I created this because I wanted a pure python language detector that doesn't require
installing a machine learning library. It was a tool that outgrew being a part
of [so_pip](https://github.com/matthewdeanmartin/so_pip) a StackOverflow code extraction tool I wrote.

This works best if you only use it for fallback, e.g. classifying code that can't
already be classified by extension or tag, or when tag is ambiguous.

# Usage
```
> code = "def yo():\n   print('hello')"
> guess_language_all_methods(code, file_name="yo.py")
["python"]
```

# How it Works
1) Inspects file extension if available.
2) Inspects shebang
3) Looks for keywords
4) Counts regexes for common patterns
5) Attemps to parse python, json, yaml
6) Inspects tags if available.

Each is imperfect and can error.

The classifier then combines the results of each using a voting algorithm.

# Docs
- [TODO](docs/TODO.md)
- [LICENSE](LICENSE)
- [Prior Art](docs/prior_art.md) Every similar project/tool

# Training Sets, Input Data
- [Rosetta Code](http://www.rosettacode.org/wiki/Rosetta_Code)
- [Reserved Keywords](https://github.com/matthewdeanmartin/Reserved-Key-Words-list-of-various-programming-languages)
- [GuessLangTools](https://github.com/yoeo/guesslangtools)  Tool for downloading examples in bulk
- [Languages + Extensions](https://gist.github.com/aymen-mouelhi/82c93fbcd25f091f2c13faa5e0d61760) in JSON form
