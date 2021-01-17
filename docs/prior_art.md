# Prior Art
Language detection is divided between libraries that are classifiers, and classifiers by accident, such as
code highlighters or line counters.

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
