UV ?= uv
MAKEFLAGS += --no-print-directory
export PYTHONUTF8 := 1

PACKAGE := whats_that_code
PYTHON_TARGETS := whats_that_code test

.PHONY: \
	sync \
	format format-check \
	lint lint-check \
	dead-code \
	test test-ci tox \
	typecheck \
	security \
	version-check dev-status \
	check check-ci \
	publish-check publish \
	dont-be-lazy pydoc-docs \
	help

help:
	@echo "Targets:"
	@echo "  sync            Install / refresh dependencies"
	@echo ""
	@echo "  format          Auto-format (black + isort)"
	@echo "  format-check    Check formatting without changes"
	@echo "  lint            pylint"
	@echo "  lint-check      pylint (read-only alias)"
	@echo ""
	@echo "  test            Run pytest suite with coverage"
	@echo "  test-ci         Run pytest -n auto (parallel, for CI)"
	@echo "  tox             Run tests across python versions via tox"
	@echo ""
	@echo "  typecheck       Run mypy"
	@echo "  security        Run bandit"
	@echo "  dead-code       Run vulture (advisory)"
	@echo ""
	@echo "  version-check   Verify version consistency (jiggle_version)"
	@echo "  dev-status      Verify Development Status classifier"
	@echo ""
	@echo "  check           Full local quality gate"
	@echo "  check-ci        CI quality gate"
	@echo "  publish-check   Build wheel and list dist/ contents"
	@echo "  publish         Publish via uv"

sync:
	@$(UV) sync --all-extras

# ── Formatting ────────────────────────────────────────────────────────────────

format:
	@$(UV) run isort $(PYTHON_TARGETS)
	@$(UV) run black $(PYTHON_TARGETS)

format-check:
	@$(UV) run isort --check-only $(PYTHON_TARGETS)
	@$(UV) run black --check $(PYTHON_TARGETS)

# ── Linting ───────────────────────────────────────────────────────────────────

lint lint-check:
	@$(UV) run pylint --score=n --reports=n $(PACKAGE)

# ── Dead code (advisory) ──────────────────────────────────────────────────────

dead-code:
	@$(UV) run vulture $(PACKAGE) --min-confidence 80 || true

# ── Tests ─────────────────────────────────────────────────────────────────────

test:
	@$(UV) run pytest -q \
		--cov=$(PACKAGE) \
		--cov-report=html \
		--junitxml=junit.xml \
		--timeout=60 \
		test/

test-ci:
	@$(UV) run pytest -q -n auto --dist=loadfile \
		--cov=$(PACKAGE) \
		--cov-report=xml \
		--junitxml=junit.xml \
		--timeout=60 \
		test/

tox:
	@$(UV) run tox

# ── Type checking ─────────────────────────────────────────────────────────────

typecheck:
	@$(UV) run mypy $(PACKAGE)

# ── Security ──────────────────────────────────────────────────────────────────

security:
	@$(UV) run bandit -q -r $(PACKAGE)

# ── Metadata / version ───────────────────────────────────────────────────────

version-check:
	@$(UV) run jiggle_version check

dev-status:
	@$(UV) run troml-dev-status validate .

# ── Release ───────────────────────────────────────────────────────────────────

publish-check:
	@$(UV) build
	@ls -lh dist/

publish:
	@$(UV) publish

# ── Gates ─────────────────────────────────────────────────────────────────────

check: lint security test typecheck version-check
	@echo "All checks passed."

check-ci: lint security test-ci typecheck version-check
	@echo "CI checks passed."

# ── Dogfooding ────────────────────────────────────────────────────────────────

dont-be-lazy:
	@$(UV) run dont_be_lazy --root . --no-color summary
	@$(UV) run dont_be_lazy --root . --no-color scan $(PACKAGE) --no-config-suppressions || true

pydoc-docs:
	@$(UV) run pydoc_fork $(PACKAGE) -o ./pydoc/
