PYTHON ?= python3

.PHONY: test bench check

test:
	$(PYTHON) -m unittest discover -s tests

bench:
	$(PYTHON) benchmark/bench.py --format markdown

check: test bench
