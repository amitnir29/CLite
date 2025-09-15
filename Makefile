.PHONY: test run examples lint

PY := python3

TEST_MODULES := \
	tests/lexer_test.py \
	tests/parser_test.py \
	tests/parser_expr_test.py \
	tests/interpreter_test.py

test:
	@set -e; \
	for t in $(TEST_MODULES); do \
		printf "Running %s...\n" $$t; \
		$(PY) -m unittest $$t -v || exit $$?; \
	done

# Usage: make run EX=examples/hello.cl [ARGS="--entry main"]
EX ?= examples/hello.cl
ARGS ?=
run:
	$(PY) -m lang.cli $(EX) $(ARGS)

examples:
	$(PY) -m lang.cli examples/hello.cl
	$(PY) -m lang.cli examples/add.cl
	$(PY) -m lang.cli examples/loop.cl
	$(PY) -m lang.cli examples/controls.cl

# Usage: make lint EX=examples/hello.cl
lint:
	$(PY) -m lang.lint_cli $(EX)
