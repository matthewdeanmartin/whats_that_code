"""Canonical language registry — single source of truth for label spellings.

This module exists to make label drift visible and to keep the set of emittable
language labels backwards compatible (the library ships ~2,000 downloads/month;
see ``spec/spec.md`` Phase 0).

Two facts about this module:

1. ``CANONICAL`` is a **frozen, hand-materialized snapshot**, not a value computed
   from the data tables at import time. That is deliberate: if it were derived from
   the tables it could never detect drift. Because it is frozen, any future edit
   that introduces a new label into a data table will fail
   ``test/test_fast/test_label_registry.py`` until the label is added here on
   purpose. The snapshot was seeded (2026-05-31) from the union of the keys of
   ``known_languages.FILE_EXTENSIONS``, ``known_languages.POPULARITY_LIST``,
   ``keyword_based.LANGUAGE_KEY_WORDS``, ``codex_markers.MARKERS`` and
   ``tags_data.RELATED_TAGS``, plus the clean language names emitted by
   ``shebang_based.SHEBANGS``.

2. It is **inventory only** — nothing here is wired into the election yet, so it
   changes no runtime behavior. Resolving a name through :func:`canonical` is
   available for later phases (label modernization) to adopt deliberately.

``ALIASES`` records genuine same-language spelling variants discovered across the
data tables. Resolving a name lowercases it first, so capitalization variants
(e.g. the ``objective-C`` key bug, see KNOWN_FINDINGS) are handled automatically.
"""

from __future__ import annotations

# Same-language spelling variants found across the data tables. Keys are the
# variant spellings (already lowercased); values are the canonical spelling that
# the registry prefers. Resolving via canonical() does NOT change what the
# election emits today — these are documentation + a hook for later phases.
ALIASES: dict[str, str] = {
    "objective-c": "objectivec",  # keyword_based spells it "objective-c"; FILE_EXTENSIONS/POPULARITY use "objectivec"
    "cpp": "c++",  # codex_markers spells it "cpp"; FILE_EXTENSIONS/keyword/popularity use "c++"
    "make": "makefile",  # codex_markers + shebang emit "make"; FILE_EXTENSIONS key is "makefile"
    ".awk": "awk",  # shebang_based stores the malformed value ".awk" (see KNOWN_FINDINGS)
}

# The frozen inventory of every canonical language label the library can emit.
# Names are lowercase and (with one legacy exception, "jupyter notebook") contain
# no spaces or dots, matching the invariants election.py enforces on votes.
# DO NOT edit casually. Adding/removing an entry is an intentional vocabulary
# change and should be reviewed alongside the data table that motivates it.
CANONICAL: frozenset[str] = frozenset(
    {
        "abap",
        "abnf",
        "actionscript",
        "actionscript3",
        "ada",
        "adl",
        "agda",
        "aheui",
        "alloy",
        "ambienttalk",
        "ampl",
        "angular2html",
        "antlractionscript",
        "antlrcpp",
        "antlrcsharp",
        "antlrjava",
        "antlrobjectivec",
        "antlrperl",
        "antlrpython",
        "antlrruby",
        "apacheconf",
        "apl",
        "applescript",
        "arduino",
        "arrow",
        "ash",
        "aspectj",
        "asymptote",
        "augeas",
        "autohotkey",
        "autoit",
        "awk",
        "bare",
        "bash",
        "bashsession",
        "batch",
        "batchfile",
        "bbcbasic",
        "bc",
        "befunge",
        "bibtex",
        "blitzbasic",
        "blitzmax",
        "bnf",
        "boa",
        "boo",
        "boogie",
        "brainfuck",
        "bst",
        "bugs",
        "c",
        "c#",
        "c++",
        "ca65",
        "cadl",
        "camkes",
        "capdl",
        "capnproto",
        "cbmbasicv2",
        "ceylon",
        "cfengine3",
        "chaiscript",
        "chapel",
        "charmci",
        "cheetah",
        "cirru",
        "clay",
        "clean",
        "clojure",
        "clojurescript",
        "cmake",
        "cobjdump",
        "cobol",
        "cobolfreeformat",
        "code",
        "coffeescript",
        "coldfusion",
        "coldfusioncfc",
        "coldfusionhtml",
        "commonlisp",
        "componentpascal",
        "coq",
        "cppobjdump",
        "cpsa",
        "crmsh",
        "croc",
        "cryptol",
        "crystal",
        "csharp",
        "csharpaspx",
        "csounddocument",
        "csoundorchestra",
        "csoundscore",
        "css",
        "cuda",
        "cypher",
        "cython",
        "d",
        "darcspatch",
        "dart",
        "dasm16",
        "debiancontrol",
        "delphi",
        "devicetree",
        "dg",
        "diff",
        "dobjdump",
        "docker",
        "dtd",
        "duel",
        "dylan",
        "dylanconsole",
        "dylanlid",
        "earlgrey",
        "easytrieve",
        "ebnf",
        "ec",
        "ecl",
        "eiffel",
        "elixir",
        "elm",
        "emacslisp",
        "email",
        "erlang",
        "erlangshell",
        "evoque",
        "evoquehtml",
        "evoquexml",
        "execline",
        "ezhil",
        "factor",
        "fancy",
        "fantom",
        "felix",
        "fennel",
        "fishshell",
        "floscript",
        "forth",
        "fortran",
        "fortranfixed",
        "foxpro",
        "freefem",
        "fsharp",
        "fstar",
        "gap",
        "gas",
        "gdscript",
        "genshi",
        "gettext",
        "gherkin",
        "glshader",
        "gnuplot",
        "go",
        "golo",
        "gooddatacl",
        "gosu",
        "gosutemplate",
        "groff",
        "groovy",
        "haml",
        "handlebarshtml",
        "haskell",
        "haxe",
        "hlslshader",
        "hsail",
        "html",
        "htmlphp",
        "hxml",
        "hy",
        "hybris",
        "icon",
        "idl",
        "idris",
        "igor",
        "inform6",
        "inform6template",
        "inform7",
        "ini",
        "io",
        "ioke",
        "irclogs",
        "isabelle",
        "j",
        "jags",
        "jasmin",
        "java",
        "javascript",
        "jcl",
        "jsgf",
        "json",
        "jsonld",
        "jsp",
        "julia",
        "jupyter notebook",
        "juttle",
        "kal",
        "kconfig",
        "kernellog",
        "koka",
        "kotlin",
        "lasso",
        "lean",
        "lesscss",
        "limbo",
        "liquid",
        "lisp",
        "literateagda",
        "literatecryptol",
        "literatehaskell",
        "literateidris",
        "livescript",
        "llvm",
        "llvmmir",
        "logos",
        "logtalk",
        "lsl",
        "lua",
        "makefile",
        "mako",
        "maql",
        "mariadb",
        "markdown",
        "mask",
        "mason",
        "mathematica",
        "matlab",
        "miniscript",
        "modelica",
        "modula2",
        "monkey",
        "monte",
        "moocode",
        "moonscript",
        "mosel",
        "mozpreproccss",
        "mozpreprocjavascript",
        "mozpreprocxul",
        "mql",
        "mscgen",
        "mupad",
        "mxml",
        "myghty",
        "nasm",
        "nasmobjdump",
        "ncl",
        "nemerle",
        "nesc",
        "newlisp",
        "newspeak",
        "nginxconf",
        "nimrod",
        "nit",
        "nix",
        "nsis",
        "nusmv",
        "objdump",
        "objectivec",
        "objectivecpp",
        "objectivej",
        "ocaml",
        "octave",
        "odin",
        "ooc",
        "opa",
        "openedge",
        "oracle",
        "pacmanconf",
        "pan",
        "parasail",
        "pawn",
        "peg",
        "perl",
        "perl6",
        "php",
        "pig",
        "pike",
        "pkgconfig",
        "pointless",
        "pony",
        "postgresql",
        "postscript",
        "povray",
        "powershell",
        "praat",
        "prolog",
        "promql",
        "properties",
        "protobuf",
        "pug",
        "puppet",
        "pypylog",
        "python",
        "python2traceback",
        "pythontraceback",
        "qbasic",
        "qml",
        "qvto",
        "r",
        "racket",
        "ragelc",
        "ragelcpp",
        "rageld",
        "ragelembedded",
        "rageljava",
        "ragelobjectivec",
        "ragelruby",
        "rconsole",
        "rd",
        "reason",
        "rebol",
        "red",
        "redcode",
        "regedit",
        "rexx",
        "rhtml",
        "ride",
        "rnccompact",
        "roboconfgraph",
        "roboconfinstances",
        "robotframework",
        "rpmspec",
        "rql",
        "rsl",
        "rst",
        "rts",
        "ruby",
        "rust",
        "s",
        "sarl",
        "sas",
        "sass",
        "scala",
        "scaml",
        "scdoc",
        "scheme",
        "scilab",
        "scss",
        "sed",
        "shell",
        "shen",
        "shexc",
        "sieve",
        "silver",
        "singularity",
        "slash",
        "slim",
        "slurmbash",
        "smali",
        "smalltalk",
        "smartgameformat",
        "smarty",
        "sml",
        "snobol",
        "snowball",
        "solidity",
        "sourcepawn",
        "sourceslist",
        "sparql",
        "sql",
        "sqlite",
        "sqliteconsole",
        "squidconf",
        "ssp",
        "stan",
        "stata",
        "supercollider",
        "swift",
        "swig",
        "systemverilog",
        "tads3",
        "tap",
        "tasm",
        "tcl",
        "tcsh",
        "teatemplate",
        "teraterm",
        "termcap",
        "terminfo",
        "terraform",
        "tex",
        "text",
        "thrift",
        "tiddlywiki5",
        "tnt",
        "todotxt",
        "toml",
        "transact-sql",
        "transactsql",
        "treetop",
        "turtle",
        "twightml",
        "typescript",
        "typoscript",
        "ucode",
        "unicon",
        "urbiscript",
        "usd",
        "vala",
        "vba",
        "vbnet",
        "vbnetaspx",
        "vbscript",
        "vcl",
        "velocity",
        "verilog",
        "vgl",
        "vhdl",
        "vim",
        "wdiff",
        "webidl",
        "whiley",
        "x10",
        "xml",
        "xorg",
        "xquery",
        "xslt",
        "xtend",
        "xtlang",
        "yaml",
        "yamljinja",
        "yang",
        "zeek",
        "zephir",
        "zig",
    }
)

# Latent issues uncovered while building this registry. These are NOT fixed here
# (fixing them changes runtime behavior); they are recorded for a later phase and
# documented in spec/phase0_findings.md.
#
# - "objective-C" (capital C) is a key in FILE_EXTENSIONS and RELATED_TAGS. If an
#   extension/tag classifier emits it, election.py raises TypeError("Bad casing").
#   canonical() resolves it (lowercases -> "objective-c" -> "objectivec").
# - shebang_based.SHEBANGS maps several interpreters to values not present in
#   FILE_EXTENSIONS (".awk", "ash", "lisp", "make", "sed"); matching one of those
#   shebangs currently raises TypeError in language_by_shebang() before returning.
# - FILE_EXTENSIONS contains both "cpp" and "c++" (and "objectivec"); they denote
#   the same languages. They remain distinct emittable labels for now.


def canonical(name: str) -> str:
    """Return the canonical spelling for ``name``.

    Lowercases and strips the input, then applies :data:`ALIASES`. Unknown names
    are returned in their normalized (lowercased/stripped) form unchanged — this
    function never raises, so callers can normalize freely.
    """
    normalized = name.strip().lower()
    return ALIASES.get(normalized, normalized)


def is_known(name: str) -> bool:
    """True if ``name`` resolves to a label in :data:`CANONICAL` (or is an alias)."""
    return canonical(name) in CANONICAL


# ── Rarity tiers (spec/spec.md Phase 2) ──────────────────────────────────────
#
# Each canonical label has a rarity tier. The tiers exist solely so a caller can
# opt out of obscure-language matches via ``Options(min_tier=...)`` (see
# whats_that_code/options.py). They change NO default behavior: tiers are only
# consulted when a caller passes a non-default ``Options`` to the election.
#
# ``TIERS`` is ordered least→most common, so ``_TIER_RANK`` gives a comparable
# integer. ``COMMON`` and ``UNCOMMON`` are curated allow-lists; everything else
# in CANONICAL (and any label not in CANONICAL at all, e.g. an arbitrary Pygments
# lexer name) is treated as ``"rare"``. These two sets are deliberately
# conservative and are expected to be *tuned* in Phase 4 using the eval harness —
# moving a label between tiers only affects the opt-in suppression path, never the
# default answer, so it is safe to adjust.
TIERS: tuple[str, str, str] = ("rare", "uncommon", "common")
_TIER_RANK: dict[str, int] = {name: rank for rank, name in enumerate(TIERS)}

# "common": the PYPL top-28 (known_languages.POPULARITY_LIST) plus the ubiquitous
# markup/config/shell languages that PYPL does not rank but that any detector must
# treat as mainstream. Both spellings of dual-spelled languages are listed so a
# match is recognized as common however it was emitted (e.g. c# / csharp).
COMMON: frozenset[str] = frozenset(
    {
        # PYPL top-28
        "python",
        "java",
        "javascript",
        "c#",
        "csharp",
        "c++",
        "php",
        "r",
        "objectivec",
        "swift",
        "typescript",
        "matlab",
        "kotlin",
        "go",
        "vba",
        "ruby",
        "rust",
        "scala",
        "vbnet",
        "lua",
        "ada",
        "dart",
        "abap",
        "perl",
        "julia",
        "groovy",
        "cobol",
        "haskell",
        "delphi",
        # ubiquitous markup / data / config / shell (not PYPL-ranked)
        "c",
        "html",
        "css",
        "json",
        "xml",
        "yaml",
        "sql",
        "bash",
        "shell",
        "markdown",
        "makefile",
        "docker",
        "ini",
        "toml",
        "powershell",
        "batch",
        "batchfile",
        "sass",
        "scss",
        "lesscss",
    }
)

# "uncommon": established languages that are widely known but not mainstream by
# PYPL standards. A caller asking for ``min_tier="uncommon"`` keeps these; one
# asking for ``min_tier="common"`` drops them (absent strong extension/shebang/tag
# evidence). Everything not in COMMON or UNCOMMON is "rare".
UNCOMMON: frozenset[str] = frozenset(
    {
        "elixir",
        "erlang",
        "clojure",
        "clojurescript",
        "fsharp",
        "ocaml",
        "scheme",
        "racket",
        "lisp",
        "commonlisp",
        "emacslisp",
        "elm",
        "crystal",
        "nimrod",
        "zig",
        "solidity",
        "terraform",
        "prolog",
        "fortran",
        "fortranfixed",
        "vala",
        "nix",
        "tcl",
        "vhdl",
        "verilog",
        "systemverilog",
        "cmake",
        "coffeescript",
        "livescript",
        "gdscript",
        "reason",
        "smalltalk",
        "d",
        "nasm",
        "gas",
    }
)


def tier(name: str) -> str:
    """Return the rarity tier (``"common"`` / ``"uncommon"`` / ``"rare"``) of a label.

    Resolves ``name`` through :func:`canonical` first, so spelling variants and
    casing are handled. Any label not explicitly listed in :data:`COMMON` or
    :data:`UNCOMMON` — including labels outside :data:`CANONICAL` entirely — is
    ``"rare"``.
    """
    resolved = canonical(name)
    if resolved in COMMON:
        return "common"
    if resolved in UNCOMMON:
        return "uncommon"
    return "rare"


def meets_tier(name: str, min_tier: str) -> bool:
    """True if ``name``'s tier is at least as common as ``min_tier``.

    e.g. ``meets_tier("zig", "common")`` is False (zig is uncommon) while
    ``meets_tier("python", "common")`` and ``meets_tier("zig", "uncommon")`` are
    True. Raises ``KeyError`` if ``min_tier`` is not one of :data:`TIERS`.
    """
    return _TIER_RANK[tier(name)] >= _TIER_RANK[min_tier]
