UV ?= uv


# ── Dogfooding targets (independent, not wired into check) ───────────────────

.PHONY: version-check
version-check:
	@$(UV) run jiggle_version check

.PHONY: dev-status
dev-status:
	@$(UV) run troml-dev-status validate .

.PHONY: prerelease-check
prerelease-check: version-check dev-status
	@echo "Pre-release checks passed."

.PHONY: dont-be-lazy
dont-be-lazy:
	@$(UV) run dont_be_lazy --root . --no-color summary
	@$(UV) run dont_be_lazy --root . --no-color scan whats_that_code --no-config-suppressions || true

.PHONY: pydoc-docs
pydoc-docs:
	@$(UV) run pydoc_fork whats_that_code -o ./pydoc/
