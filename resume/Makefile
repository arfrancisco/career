.PHONY: resume clean watch variants help

VARIANT ?= general

## Build the resume (default variant: general). Usage: make resume VARIANT=ruby
resume:
	python3 scripts/build.py $(VARIANT)

## Build every variant listed in content/variants.yaml (if that file exists)
variants:
	python3 scripts/build_all.py

## Remove all build artifacts
clean:
	rm -rf output/*.aux output/*.log output/*.out output/*.tex output/*.pdf output/*.fls output/*.fdb_latexmk

## Rebuild automatically whenever a content or template file changes
## (requires `entr`: https://github.com/eradman/entr — install via your
## package manager, e.g. `apt install entr` / `brew install entr`)
watch:
	find content templates -type f | entr -c make resume VARIANT=$(VARIANT)

help:
	@echo "Available targets:"
	@echo "  make resume [VARIANT=name]   Build a single resume variant (default: general)"
	@echo "  make variants                Build every variant defined in content/variants.yaml"
	@echo "  make clean                   Remove build artifacts from output/"
	@echo "  make watch [VARIANT=name]    Rebuild on every content/template change (needs entr)"
