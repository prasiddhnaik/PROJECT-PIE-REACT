# Project Pie Makefile
# Common development and deployment tasks

.PHONY: install install-dev test lint format clean run-dashboard run-sip run-portfolio docker-build docker-run docs help

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Project Pie - Development Commands"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"

test: ## Run test suite
	$(PYTEST) tests/ -v --cov=src

test-watch: ## Run tests in watch mode
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing -f

lint: ## Run linting checks
	$(FLAKE8) src/ tests/
	$(MYPY) src/

format: ## Format code with black
	$(BLACK) src/ tests/ scripts/

format-check: ## Check if code is formatted correctly
	$(BLACK) --check src/ tests/ scripts/

clean: ## Clean up cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/

run-dashboard: ## Run the main Streamlit dashboard
	streamlit run src/apps/streamlit_app.py

run-sip: ## Run the SIP calculator app
	streamlit run src/apps/streamlit_sip_calculator.py

run-portfolio: ## Run the portfolio analysis app
	streamlit run src/apps/streamlit_portfolio_app.py

run-fund-comparison: ## Run the fund comparison app
	streamlit run src/apps/streamlit_fund_comparison.py

run-api-dashboard: ## Run the API dashboard
	streamlit run src/apps/api_dashboard.py

stock-tracker: ## Run background stock tracker
	$(PYTHON) src/core/background_stock_tracker.py

demo-features: ## Run feature demonstrations
	$(PYTHON) src/utils/demo_features.py

quick-start: ## Quick start with setup script
	./scripts/quick_start.sh

stealth-mode: ## Run in stealth mode
	./scripts/stealth_start.sh

docker-build: ## Build Docker image
	docker build -t project-pie .

docker-run: ## Run Docker container
	docker run -p 8501:8501 project-pie

docs-build: ## Build documentation
	cd docs && make html

docs-serve: ## Serve documentation locally
	cd docs/_build/html && $(PYTHON) -m http.server 8000

setup-env: ## Set up development environment
	$(PYTHON) -m venv .venv
	@echo "Activate virtual environment with: source .venv/bin/activate"

requirements-update: ## Update requirements.txt
	$(PIP) freeze > requirements.txt

check-all: format-check lint test ## Run all quality checks

deploy-prep: clean check-all ## Prepare for deployment
	@echo "Ready for deployment!"

# Development workflow commands
dev-setup: setup-env install-dev ## Complete development setup
	@echo "Development environment ready!"

dev-run: format lint test run-dashboard ## Full development cycle

# Data management
data-backup: ## Backup data directory
	tar -czf data_backup_$(shell date +%Y%m%d_%H%M%S).tar.gz data/

data-clean: ## Clean temporary data files
	rm -rf data/cache/*
	rm -rf data/processed/*.log

# Git helpers
git-setup: ## Set up git hooks
	cp scripts/pre-commit .git/hooks/
	chmod +x .git/hooks/pre-commit

# Performance
profile: ## Profile the application
	$(PYTHON) -m cProfile -o profile.stats src/apps/streamlit_app.py

benchmark: ## Run performance benchmarks
	$(PYTHON) scripts/benchmark.py 