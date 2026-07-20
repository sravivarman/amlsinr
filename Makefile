.PHONY: sync build build-pages serve serve-pages clean consistency check

sync:
	uv sync

build:
	uv run python build.py

build-pages:
	uv run python build.py --output docs

serve:
	uv run python serve.py

serve-pages:
	uv run python serve.py 8000 docs

clean:
	rm -rf dist docs

consistency:
	uv run python tools/check_consistency.py

check: consistency build build-pages
	test -f dist/index.html
	test -f docs/index.html
	git status --short
