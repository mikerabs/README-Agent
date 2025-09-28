.PHONY: install test run clean lint

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/

run:
	python readme_hardener.py --help

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

lint:
	black .
	ruff check .

build:
	python setup.py build