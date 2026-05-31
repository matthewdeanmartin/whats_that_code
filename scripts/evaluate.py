"""Evaluation harness for whats_that_code (spec/spec.md Phase 1).

Runs the detector over a labelled corpus and reports how often it is right. This is
the standing measure-change-measure tool: every accuracy claim in later phases must
come from a number this prints. It works on any directory laid out as
``<label>/<files...>`` — the Phase 1 ``corpus/data`` *and* the Phase 0
``test/data/characterization`` corpus.

What it reports:
  * overall accuracy — strict (exact label) and lenient (clone groups counted
    equivalent: c/c++, javascript/typescript, xml/html/php);
  * per-language accuracy (n, correct, rate);
  * the worst confusions (true -> predicted pairs);
  * a machine-readable JSON report, and an optional diff vs a saved --baseline.

NOTE: detection is nondeterministic — `pyrankvote` breaks ties with the unseeded
`random` module (see spec/phase0_findings.md). This harness seeds `random` (default
``--seed 0``) so numbers are reproducible; also pin ``PYTHONHASHSEED=0`` to remove
the secondary set-ordering variance. Both are recorded in the report's _meta.

Usage:
    PYTHONHASHSEED=0 python scripts/evaluate.py                      # test split of corpus/data
    PYTHONHASHSEED=0 python scripts/evaluate.py --split dev
    python scripts/evaluate.py --corpus test/data/characterization --split all
    python scripts/evaluate.py --baseline spec/eval_baseline.json
    python scripts/evaluate.py --out spec/eval_baseline.json         # record a baseline
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from whats_that_code.election import guess_language_all_methods
from whats_that_code.known_languages import CLONES
from whats_that_code.languages import canonical
from whats_that_code.options import Options

REPO = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = REPO / "corpus" / "data"

# Eval-only synonyms layered on top of languages.canonical() (which already maps
# cpp->c++, objective-c->objectivec, make->makefile). These collapse spellings the
# detector and the corpus labels disagree on but that mean the same language.
EVAL_SYNONYMS = {
    "csharp": "c#",
    "shell": "bash",
    "sh": "bash",
}

# Lenient clone groups (a guess in the same group as the truth counts as correct).
_CLONE_GROUPS = [frozenset(canonical(x) for x in group) for group in CLONES]


def norm(label: str | None) -> str | None:
    if label is None:
        return None
    c = canonical(label)
    return EVAL_SYNONYMS.get(c, c)


def same_clone_group(a: str, b: str) -> bool:
    return any(a in g and b in g for g in _CLONE_GROUPS)


def load_targets(corpus: Path, which: str) -> list[tuple[str, Path]]:
    """Return (true_label, path) for files in the requested split."""
    split_file = corpus.parent / "split.json"
    assignment = {}
    if which != "all":
        if not split_file.exists():
            raise SystemExit(f"--split {which} needs {split_file}; run scripts/split_dataset.py (or use --split all)")
        assignment = json.loads(split_file.read_text(encoding="utf-8"))["assignment"]

    targets = []
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or path.name == "expected.json":
            continue
        rel = path.relative_to(corpus).as_posix()
        if which != "all" and assignment.get(rel) != which:
            continue
        targets.append((rel.split("/", 1)[0], path))
    return targets


def evaluate(corpus: Path, which: str, limit: int | None, seed: int | None = 0, min_tier: str | None = None) -> dict:
    # pyrankvote breaks ties with the unseeded `random` module, which is the
    # dominant source of run-to-run variance (see spec/phase0_findings.md). Seed it
    # so the harness is reproducible; pass seed=None to sample the nondeterminism.
    if seed is not None:
        random.seed(seed)
    # min_tier exercises the Phase 2 opt-in rare-language suppression. Default
    # (None) is the historical behavior; the baseline must always be recorded
    # with min_tier=None.
    options = Options(min_tier=min_tier) if min_tier is not None else None
    targets = load_targets(corpus, which)
    if limit is not None:
        # keep it stratified-ish: cap per language
        per: dict[str, int] = defaultdict(int)
        capped = []
        for label, path in targets:
            if per[label] < limit:
                capped.append((label, path))
                per[label] += 1
        targets = capped

    # Two axes: how good is it on code alone, and when also given the filename
    # (i.e. the extension). Code-only is the hard, honest metric; with-filename
    # reflects the common real-world call. Confusions/mispredictions track the
    # code-only axis (the interesting failure mode).
    axes = ("code_only", "with_filename")
    total = 0
    correct = {ax: {"strict": 0, "lenient": 0} for ax in axes}
    per_lang: dict[str, dict] = defaultdict(lambda: {"n": 0, "code_only": 0, "with_filename": 0})
    confusion: dict[str, int] = defaultdict(int)  # code-only "true>pred" -> count
    mispredictions: list[dict] = []

    for true_label, path in targets:
        code = path.read_text(encoding="utf-8", errors="ignore")
        guesses = {
            "code_only": guess_language_all_methods(code, options=options),
            "with_filename": guess_language_all_methods(code, file_name=path.name, options=options),
        }
        t = norm(true_label)
        total += 1
        per_lang[true_label]["n"] += 1
        for ax in axes:
            g = norm(guesses[ax])
            is_strict = g is not None and g == t
            is_lenient = is_strict or (g is not None and t is not None and same_clone_group(t, g))
            if is_strict:
                correct[ax]["strict"] += 1
                per_lang[true_label][ax] += 1
            if is_lenient:
                correct[ax]["lenient"] += 1
        g0 = norm(guesses["code_only"])
        if not (g0 == t or (g0 is not None and t is not None and same_clone_group(t, g0))):
            confusion[f"{t}>{g0}"] += 1
            if len(mispredictions) < 200:
                mispredictions.append({"file": path.relative_to(corpus).as_posix(), "true": t, "pred": g0})

    languages = {
        lang: {
            "n": d["n"],
            "code_only": d["code_only"],
            "with_filename": d["with_filename"],
            "code_only_rate": round(d["code_only"] / d["n"], 4) if d["n"] else 0.0,
            "with_filename_rate": round(d["with_filename"] / d["n"], 4) if d["n"] else 0.0,
        }
        for lang, d in sorted(per_lang.items())
    }
    overall = {"files": total}
    for ax in axes:
        overall[f"{ax}_strict_accuracy"] = round(correct[ax]["strict"] / total, 4) if total else 0.0
        overall[f"{ax}_lenient_accuracy"] = round(correct[ax]["lenient"] / total, 4) if total else 0.0
        overall[f"{ax}_strict_correct"] = correct[ax]["strict"]
    return {
        "_meta": {
            "corpus": str(corpus.relative_to(REPO)) if corpus.is_relative_to(REPO) else str(corpus),
            "split": which,
            "limit_per_language": limit,
            "min_tier": min_tier,
            "random_seed": seed,
            "pythonhashseed": os.environ.get("PYTHONHASHSEED", "random"),
            "files": total,
        },
        "overall": overall,
        "languages": languages,
        "top_confusions": dict(sorted(confusion.items(), key=lambda kv: -kv[1])[:25]),
        "mispredictions": mispredictions,
    }


def print_report(report: dict) -> None:
    o, m = report["overall"], report["_meta"]
    print("\n=== whats_that_code evaluation ===")
    print(f"corpus={m['corpus']} split={m['split']} files={o['files']} PYTHONHASHSEED={m['pythonhashseed']}")
    if m["pythonhashseed"] == "random":
        print(
            "  (warning: hash seed not pinned — code-only results are nondeterministic; "
            "set PYTHONHASHSEED for reproducible numbers)"
        )
    print("\n                     strict   lenient")
    print(
        f"  code only        :  {o['code_only_strict_accuracy']:5.1%}    {o['code_only_lenient_accuracy']:5.1%}"
        f"   ({o['code_only_strict_correct']}/{o['files']} strict)"
    )
    print(
        f"  with filename    :  {o['with_filename_strict_accuracy']:5.1%}    {o['with_filename_lenient_accuracy']:5.1%}"
        f"   ({o['with_filename_strict_correct']}/{o['files']} strict)"
    )

    print("\nworst languages (by code-only rate, n>=3):")
    worst = sorted(
        ((lang, d) for lang, d in report["languages"].items() if d["n"] >= 3),
        key=lambda kv: (kv[1]["code_only_rate"], -kv[1]["n"]),
    )[:15]
    for lang, d in worst:
        print(
            f"  {lang:18} code-only {d['code_only_rate']:4.0%}  with-file {d['with_filename_rate']:4.0%}  (n={d['n']})"
        )

    print("\ntop code-only confusions (true > predicted : count):")
    for pair, count in list(report["top_confusions"].items())[:15]:
        print(f"  {pair:40} {count}")


def diff_baseline(report: dict, baseline_path: Path) -> None:
    base = json.loads(baseline_path.read_text(encoding="utf-8"))
    b, c = base["overall"], report["overall"]
    print(f"\n=== diff vs {baseline_path.name} ===")
    for key in (
        "code_only_strict_accuracy",
        "code_only_lenient_accuracy",
        "with_filename_strict_accuracy",
        "with_filename_lenient_accuracy",
    ):
        delta = c[key] - b.get(key, 0.0)
        arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "=")
        print(f"  {key:32} {b.get(key, 0.0):.1%} -> {c[key]:.1%}  {arrow} {delta:+.1%}")
    # per-language code-only regressions
    regressions = []
    for lang, cd in report["languages"].items():
        bd = base["languages"].get(lang)
        if bd and cd["n"] and bd["n"]:
            d = cd["code_only_rate"] - bd["code_only_rate"]
            if d < -0.001:
                regressions.append((lang, bd["code_only_rate"], cd["code_only_rate"], d))
    if regressions:
        print("  per-language code-only regressions:")
        for lang, was, now, d in sorted(regressions, key=lambda r: r[3])[:15]:
            print(f"    {lang:18} {was:.0%} -> {now:.0%}  ({d:+.0%})")
    else:
        print("  no per-language code-only regressions.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--split", default="test", choices=["train", "dev", "test", "all"])
    parser.add_argument("--limit", type=int, default=None, help="cap files per language")
    parser.add_argument("--out", type=Path, default=None, help="write JSON report here")
    parser.add_argument("--baseline", type=Path, default=None, help="diff overall + per-language vs this report")
    parser.add_argument("--seed", type=int, default=0, help="seed for pyrankvote tie-breaks (-1 = don't seed)")
    parser.add_argument(
        "--min-tier",
        default=None,
        choices=["common", "uncommon", "rare"],
        help="Phase 2 rare-language suppression (Options(min_tier=...)); default off = historical behavior",
    )
    args = parser.parse_args(argv)

    if not args.corpus.exists():
        print(f"No corpus at {args.corpus}. Run scripts/build_dataset.py first.")
        return 1

    seed = None if args.seed == -1 else args.seed
    report = evaluate(args.corpus, args.split, args.limit, seed=seed, min_tier=args.min_tier)
    print_report(report)
    if args.baseline and args.baseline.exists():
        diff_baseline(report, args.baseline)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
