.PHONY: sync build serve clean consistency check

sync:
	uv sync

build:
	uv run python build.py

serve:
	uv run python serve.py

clean:
	rm -rf dist docs

consistency:
	uv run python tools/check_consistency.py

check: consistency build
	test -f dist/index.html
	git status --short
