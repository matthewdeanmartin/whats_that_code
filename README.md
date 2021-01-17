# whats_that_code
This is a programming langauge detection library.

It will detect programming language of source in pure python from an ensemble of classifiers

It aims to detect languages when a quick and dirty first approximation is good enough.

I created this because I wanted a pure python language detector that doesn't require
installing a machine learning library.

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


# Prior Art
Languae detection is divided between libraries that are primarily trying to format and colorize code
and libraries that are detecting code.

Python
- [Guesslang](https://pypi.org/project/guesslang/) - python and tensorflow driven solution.
- [Deep Learning](https://github.com/tunafield/deep-learning-lang-detection) - keras and tensor flow.
- [Programming Language Detection](https://github.com/batogov/programming-language-detection) - sklearn based
- [Codex](https://github.com/TomCrypto/Codex) - sklearn based
- [Code Sleuth](https://github.com/scivision/code-sleuth) - Currently only detects language by project file?

Not Python
- [Language Detection EL](https://github.com/andreasjansson/language-detection.el) - Lisp. Editor plugin
- [Github's Linguist](https://github.com/github/linguist) Ruby. Classifies code in repos.
- [Source Classifier](https://github.com/chrislo/sourceclassifier) Ruby.
- [Code Classifier](https://github.com/bertyhell/CodeClassifier) C#.

Highlight/Formatter/Line Counter/Decompilation
- [highlight.js](https://github.com/highlightjs/highlight.js). Javascript
- [code-prettify](https://github.com/googlearchive/code-prettify). Javascript.
- [pygments](https://pygments.org/docs/api/#pygments.lexers.guess_lexer). Python
- [OhCount](https://github.com/blackducksoftware/ohcount) Ruby.
- [IDAPro](https://www.hex-rays.com/products/ida/) Commercial decompiler. Identifies langauge of binary code.

Research Papers, possibly with no public source
- [Predicting SO](https://www.researchgate.net/publication/338132359_SCC_Predicting_the_Programming_Language_of_Questions_and_Snippets_of_StackOverflow)
- [Github's OctoLingua](https://github.com/MankaranSingh/GSoC-2020/blob/master/README.md) Closed source classifier?

## Resources
# Training Sets
- [Rosetta Code](http://www.rosettacode.org/wiki/Rosetta_Code)
- [Reserved Keywords](https://github.com/matthewdeanmartin/Reserved-Key-Words-list-of-various-programming-languages)
- [GuessLangTools](https://github.com/yoeo/guesslangtools)  Tool for downloading examples in bulk
- [Languages + Extensions](https://gist.github.com/aymen-mouelhi/82c93fbcd25f091f2c13faa5e0d61760) in JSON form
