"""Deterministic train/dev/test split for the corpus (spec/spec.md Phase 1).

Writes corpus/split.json mapping each corpus file to "train", "dev", or "test".
The split is a pure function of the file path (a hashed bucket), so it is:

  * reproducible — same corpus always yields the same split, no stored RNG state;
  * stratified — bucketing is per-language, so each split sees every language;
  * stable — adding files for one language doesn't reshuffle the others.

Accuracy must be reported on "test" (or "dev" during tuning) so that improvements
are not validated on data they were tuned against.

Usage:
    python scripts/split_dataset.py                       # 70/15/15 by default
    python scripts/split_dataset.py --ratios 60 20 20
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus"
DATA = CORPUS / "data"
SPLIT = CORPUS / "split.json"
SALT = "whats_that_code/phase1/v1"  # bump to deliberately reshuffle every split


def _bucket(relpath: str) -> float:
    """Stable float in [0, 1) derived from the file path (seed-independent)."""
    digest = hashlib.sha256((SALT + relpath).encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def iter_corpus(data: Path):
    for path in sorted(data.rglob("*")):
        if path.is_file():
            yield path.relative_to(data).as_posix()


def build_split(data: Path, ratios: tuple[float, float, float]) -> dict:
    train_r, dev_r, _test_r = ratios
    by_lang: dict[str, list[str]] = defaultdict(list)
    for rel in iter_corpus(data):
        by_lang[rel.split("/", 1)[0]].append(rel)

    assignment: dict[str, str] = {}
    counts = {"train": 0, "dev": 0, "test": 0}
    for _lang, rels in by_lang.items():
        for rel in rels:
            b = _bucket(rel)
            if b < train_r:
                split = "train"
            elif b < train_r + dev_r:
                split = "dev"
            else:
                split = "test"
            assignment[rel] = split
            counts[split] += 1
    return {
        "salt": SALT,
        "ratios": {"train": ratios[0], "dev": ratios[1], "test": ratios[2]},
        "counts": counts,
        "languages": len(by_lang),
        "assignment": dict(sorted(assignment.items())),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ratios", type=float, nargs=3, default=[70, 15, 15], metavar=("TRAIN", "DEV", "TEST"))
    parser.add_argument("--data", type=Path, default=DATA, help="corpus data dir")
    args = parser.parse_args(argv)

    if not args.data.exists():
        print(f"No corpus at {args.data}. Run scripts/build_dataset.py first.")
        return 1

    total = sum(args.ratios)
    ratios = (args.ratios[0] / total, args.ratios[1] / total, args.ratios[2] / total)
    split = build_split(args.data, ratios)
    SPLIT.write_text(json.dumps(split, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {SPLIT}")
    print(f"  languages: {split['languages']}")
    print(f"  train/dev/test: {split['counts']['train']}/{split['counts']['dev']}/{split['counts']['test']}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
