.PHONY: help install run test clean lint format

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

run: ## Run the API server
	python api.py

test: ## Run unit tests
	.venv\Scripts\python.exe -m pytest tests/test_api.py -v

test-coverage: ## Run tests with coverage
	.venv\Scripts\python.exe -m pytest tests/test_api.py --cov=. --cov-report=html

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code with black
	black .

check-format: ## Check code formatting
	black --check .

type-check: ## Run type checking with mypy
	mypy . --ignore-missing-imports

dev-setup: ## Setup development environment
	pip install black flake8 mypy pytest-cov
	pre-commit install

docker-build: ## Build Docker image
	docker build -t arabic-ocr-api .

docker-run: ## Run Docker container
	docker run -p 8000:8000 arabic-ocr-api