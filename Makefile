# Makefile for Memory Classification Engine

.PHONY: install test coverage clean lint

install:
	pip install -e .

install-dev:
	pip install -e .[dev]

test:
	python -m pytest tests/

coverage:
	python -m pytest tests/ --cov=memory_classification_engine --cov-report=html

clean:
	rm -rf ./data ./htmlcov ./coverage.xml

lint:
	flake8 src/

format:
	black src/ tests/

run:
	python -c "from memory_classification_engine import MemoryClassificationEngine; engine = MemoryClassificationEngine(); print('Engine initialized successfully!')"
