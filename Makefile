.PHONY: help
help:  ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup:  ## Set up the local development environment
	poetry install
	poetry run pre-commit install

.PHONY: tox
test:  ## Run the tests
	poetry run tox

.PHONY: publish
publish:  ## Build & publish the new version
	poetry build
	poetry publish

.PHONY: build-docs
build-docs: docs/autogen-requirements.txt  ## Build the Sphinx docs
	sphinx-build -M html docs docs/_build

.PHONY: serve-docs
serve-docs: build-docs  ## Simple development server for Sphinx docs
	@echo "Serving documentation locally."
	@echo "Open browser with 'make open-docs'"
	@find docs toml_sort | entr -ps "$(MAKE) build-docs"

.PHONY: open-docs
open-docs:  ## Open Sphinx docs index in a browser
	gio open docs/_build/html/index.html

docs/autogen-requirements.txt:  ## Autogenerate the requirements.txt
	poetry export --dev --format requirements.txt --output $@ && git add $@
	exit 1
