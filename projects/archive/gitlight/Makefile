FLASK_APP ?= gitlight.app:create_app()
FLASK_ENV ?= development
CODACYCOV += no
export FLASK_APP FLASK_ENV CODACYCOV

# Clean up build/cache data
clean:
	@# Python cache
	@find . -name '*.pyc' \
		-o -name '__pycache__' \
		-o -name '.pytest_cache' \
		-exec rm -rf {} \;
	@# Generated documentation
	@find docs/ref/ -mindepth 1 -type d -exec rm -rf {} +;
	@# Build artifacts
	@rm -rf _build

# Create an output directory
_build:
	@mkdir _build

# Run a development web server
#   -r requirements/base.txt
run:
	flask run

# Build local copy of documentation
#   -r requirements/docs.txt
docs: _build
	sphinx-build docs/ _build/docs/

# Run tests
#   -r requirements/tests.txt
# Running 'pytest' may be more efficient.
# It supports options like --skip-slow (See: pytest --help).
test:
	pytest

# Spell checker (pytest-spellcheck would be better)
#   -r requirements/tests.txt
spell: _build
	find gitlight/ -name '*.py' | misspellings -f - | tee _build/spelling.txt

# Lint checker
#   -r requirements/tests.txt
lint: _build
	pylint --jobs=0 --persistent=n gitlight | tee _build/lint.txt

# Build code coverage map
#   -r requirements/tests.txt
coverage: _build
	pytest \
		--cov-config tests/.coveragerc \
		--cov-report=xml \
		--cov-report=html \
		--cov-report=term:skip-covered \
		--cov=gitlight tests/ \
			>_build/coverage.txt

# Print coverage to console
cov-text: coverage
	awk '/- coverage:/{y=1;next}y' _build/coverage.txt

# Open coverage in browser
cov-html: coverage
	sensible-browser _build/htmlcov/index.html

.PHONY: clean run docs test spell lint coverage cov-text cov-html
