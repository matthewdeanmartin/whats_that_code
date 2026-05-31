"""Performance profiler for whats_that_code (spec/spec.md Phase 3).

No optimization is accepted without a before/after number from this script. It
reports two things:

  * import time — how long ``import whats_that_code.election`` takes cold (measured
    in a fresh subprocess so module caching doesn't hide it);
  * per-call latency — median and p95 wall-clock for ``guess_language_all_methods``
    over a representative sample of the corpus, on both axes (code-only and
    with-filename) and with cProfile's top cumulative functions.

Usage:
    python scripts/profile.py                      # uses corpus/data if present, else built-ins
    python scripts/profile.py --limit 5            # files per language
    python scripts/profile.py --use-parsers        # also exercise the opt-in parser path
    python scripts/profile.py --profile            # print cProfile hot spots
"""

from __future__ import annotations

import argparse
import contextlib
import cProfile
import io
import pstats
import statistics
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

REPO = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = REPO / "corpus" / "data"

# A few built-in snippets so the profiler runs even without a corpus checked out.
BUILTINS = [
    ("hello.py", "def main():\n    print('hello')\n\nif __name__ == '__main__':\n    main()\n"),
    ("a.js", "function add(a, b) {\n  return a + b;\n}\nconsole.log(add(1, 2));\n"),
    ("q.sql", "SELECT id, name FROM users WHERE active = 1 ORDER BY name;\n"),
    ("c.c", '#include <stdio.h>\nint main(void){ printf("hi\\n"); return 0; }\n'),
    ("x.rb", "class Greeter\n  def hello\n    puts 'hi'\n  end\nend\n"),
]


def measure_import_time(reps: int = 5) -> float:
    """Median cold-import time of the package's main entry, in milliseconds."""
    times = []
    for _ in range(reps):
        out = subprocess.run(
            [sys.executable, "-X", "importtime", "-c", "import whats_that_code.election"],
            capture_output=True,
            text=True,
            check=True,
        )
        # the last 'import time' self+cumulative line for the package, in microseconds
        total_us = 0
        for line in out.stderr.splitlines():
            if "whats_that_code.election" in line and "|" in line:
                # columns: self | cumulative | name
                parts = [p.strip() for p in line.split("|")]
                with contextlib.suppress(ValueError, IndexError):
                    total_us = int(parts[1])  # cumulative
        times.append(total_us / 1000.0)
    return statistics.median(times)


def load_samples(corpus: Path, limit: int) -> list[tuple[str, str]]:
    if not corpus.exists():
        return BUILTINS
    samples: list[tuple[str, str]] = []
    per: dict[str, int] = {}
    for path in sorted(corpus.rglob("*")):
        if not path.is_file() or path.name == "expected.json":
            continue
        lang = path.relative_to(corpus).parts[0]
        if per.get(lang, 0) >= limit:
            continue
        per[lang] = per.get(lang, 0) + 1
        samples.append((path.name, path.read_text(encoding="utf-8", errors="ignore")))
    return samples or BUILTINS


def time_axis(samples, fn) -> tuple[float, float, float]:
    """Return (median_ms, p95_ms, total_s) for calling fn(name, code) over samples."""
    durations = []
    t0 = time.perf_counter()
    for name, code in samples:
        s = time.perf_counter()
        fn(name, code)
        durations.append((time.perf_counter() - s) * 1000.0)
    total = time.perf_counter() - t0
    durations.sort()
    p95 = durations[min(len(durations) - 1, int(len(durations) * 0.95))] if durations else 0.0
    return (statistics.median(durations) if durations else 0.0, p95, total)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--limit", type=int, default=5, help="files per language")
    parser.add_argument("--use-parsers", action="store_true", help="exercise the opt-in parser path")
    parser.add_argument("--profile", action="store_true", help="print cProfile hot spots")
    args = parser.parse_args(argv)

    # Import after path setup; importing here (not at top) keeps measure_import_time honest.
    from whats_that_code.election import guess_language_all_methods
    from whats_that_code.options import Options

    samples = load_samples(args.corpus, args.limit)
    opts = Options(use_parsers=True) if args.use_parsers else None

    print(f"\n=== whats_that_code profile === ({len(samples)} samples, use_parsers={args.use_parsers})")
    import_ms = measure_import_time()
    print(f"cold import (median of 5): {import_ms:.1f} ms")

    code_only = time_axis(samples, lambda _n, c: guess_language_all_methods(c, options=opts))
    with_file = time_axis(samples, lambda n, c: guess_language_all_methods(c, file_name=n, options=opts))
    print("\n                 median     p95     total")
    print(f"  code only   : {code_only[0]:7.2f} {code_only[1]:7.2f} ms   {code_only[2]:6.2f} s")
    print(f"  with file   : {with_file[0]:7.2f} {with_file[1]:7.2f} ms   {with_file[2]:6.2f} s")

    if args.profile:
        prof = cProfile.Profile()
        prof.enable()
        for _name, code in samples:
            guess_language_all_methods(code, options=opts)
        prof.disable()
        buf = io.StringIO()
        pstats.Stats(prof, stream=buf).sort_stats("cumulative").print_stats(15)
        print("\n=== cProfile (code-only, top cumulative) ===")
        print(buf.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
