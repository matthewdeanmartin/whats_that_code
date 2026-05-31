#!/usr/bin/env bash
# Smoke test: exercises the CLI arg parser and verifies basic invocations exit cleanly.
# Counts successes and failures; exits non-zero if any check failed.
# Source an already-active venv before running, or call via `uv run bash scripts/basic_checks.sh`.

set -ou pipefail

PASS=0
FAIL=0
CLI_PYTHON="${PYTHON:-python}"

# This script itself is used as a known bash file input.
THIS_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

run_cli() {
    "$CLI_PYTHON" -m whats_that_code "$@"
}

check() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  PASS: $desc"
        ((PASS++))
    else
        echo "  FAIL: $desc  (cmd: $*)"
        ((FAIL++))
    fi
}

check_fails() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  FAIL: $desc  (expected non-zero exit, got 0)"
        ((FAIL++))
    else
        echo "  PASS: $desc"
        ((PASS++))
    fi
}

check_output() {
    local desc="$1"
    local expected="$2"
    shift 2
    local actual
    actual=$("$@" 2>/dev/null)
    if [ "$actual" = "$expected" ]; then
        echo "  PASS: $desc"
        ((PASS++))
    else
        echo "  FAIL: $desc  (expected '$expected', got '$actual')"
        ((FAIL++))
    fi
}

echo "=== whats_that_code basic_checks ==="
echo ""
echo "using: ${CLI_PYTHON} -m whats_that_code"
echo ""

echo "--- global flags ---"
check       "whats_that_code --help"    run_cli --help
check       "whats_that_code --version" run_cli --version

echo ""
echo "--- -c / --code: inline snippets ---"
check_output "python snippet identified"  "python"  run_cli --code 'def foo(): return 42'
check_output "bash snippet identified"    "bash"    run_cli --code $'#!/usr/bin/env bash\necho hello'
check_output "json snippet identified"   "json"    run_cli --code '{"key": "value"}'
check_output "javascript snippet"        "javascript" run_cli --code 'function hello() { console.log("world"); }'
check_output "--code long-form works"    "python"  run_cli --code 'import os\nprint(os.getcwd())'

echo ""
echo "--- --verbose flag ---"
check "verbose with python snippet"  run_cli --verbose --code 'def bar(): pass'
check "verbose with bash snippet"    run_cli --verbose --code $'#!/usr/bin/env bash\nls -la'

echo ""
echo "--- -f / --file: file detection (read-only, no dry-run needed) ---"
check_output "bash script detected from file"   "bash"   run_cli --file "$THIS_SCRIPT"
check_output "python file detected from file"   "python" run_cli --file "$(dirname "$THIS_SCRIPT")/../whats_that_code/__main__.py"
check_output "--file long-form works"           "python" run_cli --file "$(dirname "$THIS_SCRIPT")/../whats_that_code/election.py"
check "verbose + file"  run_cli --verbose --file "$THIS_SCRIPT"

echo ""
echo "--- error cases (must exit non-zero) ---"
check_fails "no arguments → error"          run_cli
check_fails "--code and --file mutual exclusion" run_cli --code 'x=1' --file "$THIS_SCRIPT"
check_fails "missing file → error"          run_cli --file /nonexistent/path/to/file.py

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
