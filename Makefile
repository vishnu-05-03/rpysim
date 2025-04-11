PYTHON = python3
PYTEST = $(PYTHON) -m pytest
COVERAGE_DIR = coverage_output

.PHONY: test test-cov clean test-single

# Create necessary directories
$(COVERAGE_DIR):
	mkdir -p $(COVERAGE_DIR)

# Run tests without coverage - use standard pytest pattern matching
test:
	$(PYTEST) tests/*Test.py -v

# Run a single test file
test-single:
	@if [ -z "$(TEST)" ]; then \
		echo "Usage: make test-single TEST=TestName (without .py extension)"; \
		exit 1; \
	fi
	$(PYTEST) tests/$(TEST).py -v

# Run tests with coverage for Memory module
test-cov: $(COVERAGE_DIR)
	$(PYTEST) tests/MemoryTest.py \
		--cov=src.Memory \
		--cov-report term \
		--cov-report html:$(COVERAGE_DIR)/html \
		--cov-report xml:$(COVERAGE_DIR)/coverage.xml \
		--cov-config=.coveragerc \
		-v

# Run tests with coverage for all modules - use standard pytest pattern matching
test-all-cov: $(COVERAGE_DIR)
	$(PYTEST) tests/*Test.py \
		--cov=src \
		--cov-report term \
		--cov-report html:$(COVERAGE_DIR)/html \
		--cov-report xml:$(COVERAGE_DIR)/coverage.xml \
		--cov-config=.coveragerc \
		-v

# Clean up generated files
clean:
	rm -rf $(COVERAGE_DIR) .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
