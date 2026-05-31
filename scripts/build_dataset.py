"""Rebuild the labelled corpus for whats_that_code (spec/spec.md Phase 1).

The original training/eval corpora referenced in docs/Data.md are no longer on
disk. This script re-fetches a labelled corpus from public sources and normalizes
it to a flat, canonical-language layout that the evaluation harness
(scripts/evaluate.py) and the slow test consume:

    corpus/data/<canonical_language>/<source>__<sanitized_original_path>

Only the *builder* and the *manifest* are committed — never the corpus itself
(size + per-source licensing). The corpus directory is gitignored.

Primary source: GitHub Linguist `samples/` (well organized: one directory per
language). Fetched with a shallow, blobless, sparse clone so we only download the
samples tree. Additional sources can be added to SOURCES.

Usage:
    python scripts/build_dataset.py                 # full build (all mapped languages)
    python scripts/build_dataset.py --limit 25      # cap files per language (fast baseline)
    python scripts/build_dataset.py --sources linguist
    python scripts/build_dataset.py --keep-sources  # don't delete the clones afterward
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Make the package importable when run from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from whats_that_code.languages import canonical, is_known

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus"
DATA = CORPUS / "data"
SOURCES_DIR = CORPUS / "_sources"
MANIFEST = CORPUS / "MANIFEST.json"

# ── Source definitions ───────────────────────────────────────────────────────

SOURCES = {
    "linguist": {
        "url": "https://github.com/github-linguist/linguist.git",
        "samples_subdir": "samples",
        # Linguist samples are community-contributed; licensing is per-file/mixed.
        # Used here only for local evaluation, never redistributed.
        "license": "MIT (tool) / mixed per-sample — local evaluation use only",
    },
}

# Linguist language directory names whose lowercased form is NOT already a known
# canonical label. Everything else falls back to languages.canonical(name).
LINGUIST_LANG_MAP = {
    "shell": "bash",
    "f#": "fsharp",
    "common lisp": "commonlisp",
    "emacs lisp": "emacslisp",
    "newlisp": "newlisp",
    "visual basic .net": "vbnet",
    "visual basic": "vbnet",
    "vba": "vba",
    "objective-c++": "objectivecpp",
    "jupyter notebook": "jupyter notebook",
    "restructuredtext": "rst",
    "gettext catalog": "gettext",
    "unix assembly": "gas",
    "assembly": "nasm",
    "raku": "perl6",
    "pascal": "delphi",
    "pov-ray sdl": "povray",
    "wolfram language": "mathematica",
}


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=None if cwd is None else str(cwd), check=True)


def sparse_clone_samples(name: str, spec: dict) -> Path:
    """Shallow/blobless/sparse clone of just the samples subdir. Returns its path."""
    dest = SOURCES_DIR / name
    samples = dest / spec["samples_subdir"]
    if samples.exists():
        print(f"[{name}] reusing existing clone at {dest}")
        return samples
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    print(f"[{name}] sparse-cloning {spec['url']} (samples only)…")
    _run(["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", spec["url"], str(dest)])
    _run(["git", "sparse-checkout", "set", spec["samples_subdir"]], cwd=dest)
    _run(["git", "checkout"], cwd=dest)
    return samples


def source_commit(name: str) -> str:
    dest = SOURCES_DIR / name
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(dest), capture_output=True, text=True, check=True)
    return out.stdout.strip()


def map_language(source: str, raw_name: str) -> str | None:
    """Map a source-specific language directory name to a canonical label, or None."""
    key = raw_name.strip().lower()
    if source == "linguist" and key in LINGUIST_LANG_MAP:
        return LINGUIST_LANG_MAP[key]
    resolved = canonical(raw_name)
    return resolved if is_known(resolved) else None


def _sanitize(rel: str) -> str:
    return rel.replace("/", "_").replace("\\", "_").replace(" ", "_")


def ingest_linguist(samples: Path, limit: int | None) -> tuple[dict[str, int], dict[str, int]]:
    """Copy samples into corpus/data/<canonical>/. Returns (included_counts, skipped_counts)."""
    included: dict[str, int] = {}
    skipped: dict[str, int] = {}
    for lang_dir in sorted(p for p in samples.iterdir() if p.is_dir()):
        label = map_language("linguist", lang_dir.name)
        if label is None:
            skipped[lang_dir.name] = sum(1 for f in lang_dir.rglob("*") if f.is_file())
            continue
        out_dir = DATA / label
        out_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for src_file in sorted(f for f in lang_dir.rglob("*") if f.is_file()):
            if limit is not None and count >= limit:
                break
            rel = src_file.relative_to(lang_dir).as_posix()
            dest = out_dir / f"linguist__{_sanitize(rel)}"
            try:
                shutil.copyfile(src_file, dest)
            except OSError:
                continue
            count += 1
        if count:
            included[label] = included.get(label, 0) + count
        else:
            out_dir.rmdir() if not any(out_dir.iterdir()) else None
    return included, skipped


def build(source_names: list[str], limit: int | None, keep_sources: bool) -> dict:
    if DATA.exists():
        shutil.rmtree(DATA)
    DATA.mkdir(parents=True, exist_ok=True)

    manifest: dict = {
        "generated": datetime.now(UTC).isoformat(),
        "limit_per_language": limit,
        "sources": {},
        "languages": {},
        "skipped_languages": {},
        "totals": {},
    }
    all_included: dict[str, int] = {}
    for name in source_names:
        spec = SOURCES[name]
        samples = sparse_clone_samples(name, spec)
        if name == "linguist":
            included, skipped = ingest_linguist(samples, limit)
        else:  # pragma: no cover - future sources
            raise NotImplementedError(name)
        manifest["sources"][name] = {
            "url": spec["url"],
            "commit": source_commit(name),
            "license": spec["license"],
            "languages": len(included),
            "files": sum(included.values()),
        }
        manifest["skipped_languages"][name] = dict(sorted(skipped.items()))
        for label, n in included.items():
            all_included[label] = all_included.get(label, 0) + n
        if not keep_sources:
            shutil.rmtree(SOURCES_DIR / name, ignore_errors=True)

    manifest["languages"] = dict(sorted(all_included.items()))
    manifest["totals"] = {
        "languages": len(all_included),
        "files": sum(all_included.values()),
    }
    CORPUS.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--sources", nargs="+", default=["linguist"], choices=sorted(SOURCES), help="sources to build from"
    )
    parser.add_argument("--limit", type=int, default=None, help="max files per language (default: all)")
    parser.add_argument(
        "--keep-sources", action="store_true", help="keep the cloned source repos under corpus/_sources/"
    )
    args = parser.parse_args(argv)

    manifest = build(args.sources, args.limit, args.keep_sources)
    print(f"\nWrote {MANIFEST}")
    print(f"  languages: {manifest['totals']['languages']}")
    print(f"  files:     {manifest['totals']['files']}")
    skipped_total = sum(len(v) for v in manifest["skipped_languages"].values())
    print(f"  skipped (unmapped) language dirs: {skipped_total}")
    print(f"\nCorpus at {DATA} (gitignored). Next: python scripts/split_dataset.py && python scripts/evaluate.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
