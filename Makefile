.PHONY: setup data analysis clean test help

# Default target
help:
	@echo "EMS Readiness Optimization - Available targets:"
	@echo "  setup    - Create virtual environment and install dependencies"
	@echo "  data     - Process raw data files"
	@echo "  analysis - Run the full analysis pipeline"
	@echo "  test     - Run unit tests"
	@echo "  clean    - Remove generated files"
	@echo "  help     - Show this help message"

# Create virtual environment and install dependencies
setup:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Setup complete. Activate with: source venv/bin/activate"

# Process raw data
data:
	@echo "Processing raw data..."
	. venv/bin/activate && python src/ems_readiness/data_processing.py
	@echo "Data processing complete."

# Run full analysis pipeline
analysis: data
	@echo "Running analysis..."
	. venv/bin/activate && python src/ems_readiness/analysis.py
	@echo "Analysis complete. Results saved to results/"

# Run tests
test:
	@echo "Running tests..."
	. venv/bin/activate && pytest tests/ -v

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf data/interim/*
	rm -rf data/processed/*
	rm -rf results/figures/*
	rm -rf results/maps/*
	rm -rf results/tables/*
	rm -rf __pycache__
	rm -rf src/ems_readiness/__pycache__
	rm -rf .pytest_cache
	rm -rf .ipynb_checkpoints
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	# Keep .gitkeep files
	touch data/interim/.gitkeep
	touch data/processed/.gitkeep
	touch results/figures/.gitkeep
	touch results/maps/.gitkeep
	touch results/tables/.gitkeep
	@echo "Clean complete."
