# TODO

## Release 1.0 goals
- performance tuning
- gather information on voter algorithms (do they ever tip elections)
- packaging
- a few more usage examples
- implement safe json/yaml/xml parser (others?)
- explicitly deal with "clones" (e.g. c is valid c++, javascript is valid TypeScript)

## Release 2.0 goals
- popularity vote (i.e. boost guesses if the guess is a top 20 popular language)
- refactor language data (name & alts, extension & alts, tags & alts)
- improve tag based using StackOverflow data, e.g. numpy tag is probably python code
- improve shebang code to cover more

## Release 3.0 goals
- Classify code vs not-code, e.g. code of unknown language vs probably orindary english.
    - ref: https://softwareengineering.stackexchange.com/questions/87611/simple-method-for-reliably-detecting-code-in-text
- Detect language of a collection of files, e.g. detect a python package (which could contain other files)
