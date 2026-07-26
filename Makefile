.PHONY: help install install-dev test clean lint format

help:
	@echo "Supercode - Available commands:"
	@echo "  make install        - Install the project"
	@echo "  make install-dev    - Install with development dependencies"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r requirements-dev.txt 2>/dev/null || echo "No requirements-dev.txt found"

test:
	python -m pytest

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

lint:
	python -m pylint supercode/ 2>/dev/null || echo "pylint not installed"
	python -m flake8 supercode/ 2>/dev/null || echo "flake8 not installed"

format:
	python -m black supercode/ 2>/dev/null || echo "black not installed"
	python -m isort supercode/ 2>/dev/null || echo "isort not installed"
