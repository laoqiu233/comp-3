CODE = comp3
DEFAULT_OUTPUT = output.json

LISQ_SOURCE_FILES = $(shell find examples -name *.lisq)
LISQ_COMPILED_FILES = $(patsubst %.lisq, output/%.json, $(LISQ_SOURCE_FILES))

all: $(LISQ_COMPILED_FILES)

format:
	poetry run python -m isort $(CODE)
	poetry run python -m black $(CODE)

lint:
	poetry run python -m pylint $(CODE)

output/%.json: %.lisq
	poetry run python -m comp3.compiler $< $@