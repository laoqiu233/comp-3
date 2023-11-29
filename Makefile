APPLICATION_NAME = comp3
CODE = $(APPLICATION_NAME) tests
DEFAULT_OUTPUT = output.json

LISQ_SOURCE_FILES = $(shell find examples -name *.lisq)
LISQ_COMPILED_FILES = $(patsubst %.lisq, output/%.json, $(LISQ_SOURCE_FILES))

TEST_ARGS = --verbosity=2 --showlocals --log-level=DEBUG

all: $(LISQ_COMPILED_FILES)

format:
	poetry run python -m isort $(CODE)
	poetry run python -m black $(CODE)

lint:
	poetry run python -m pylint $(CODE)

clean:
	rm -rf output

test:
	poetry run python -m pytest $(TEST_ARGS)

test-cov:
	poetry run python -m pytest $(TEST_ARGS) --cov=$(APPLICATION_NAME) --cov-fail-under=70

test-cov-html:
	poetry run python -m pytest $(TEST_ARGS) --cov=$(APPLICATION_NAME) --cov-report html --cov-fail-under=70

update-goldens:
	poetry run python -m pytest --update-goldens

output/%.json: %.lisq
	poetry run python -m comp3.compiler $< $@