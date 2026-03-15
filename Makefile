.PHONY: setup data clean-data verify-data analysis clean test help

# Default target
help:
	@echo "EMS Readiness Optimization - Available targets:"
	@echo "  setup       - Create virtual environment and install dependencies"
	@echo "  data        - Generate all processed data from raw inputs"
	@echo "  clean-data  - Remove all processed/generated data files"
	@echo "  verify-data - Check if all processed data files exist"
	@echo "  analysis    - Run the full analysis pipeline"
	@echo "  test        - Run unit tests"
	@echo "  clean       - Remove all generated files (data + results + caches)"
	@echo "  help        - Show this help message"

# Create virtual environment and install dependencies
setup:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Setup complete. Activate with: source venv/bin/activate"

# Generate all processed data from raw inputs
data:
	@echo "Generating processed data from raw inputs..."
	python scripts/generate_all_data.py
	@echo "Data generation complete."

# Remove all processed/generated data (keeps raw + reference)
clean-data:
	@echo "Removing processed data..."
	rm -f data/processed/*.csv
	rm -f data/processed/*.parquet
	rm -f data/processed/*.geojson
	rm -f data/processed/*.json
	rm -f data/processed/cache/*.pkl
	rm -f data/raw/*.pkl
	rm -f data/manifests/*.csv
	@echo "Processed data removed. Run 'make data' to regenerate."

# Verify all processed data files exist
verify-data:
	python scripts/generate_all_data.py --verify

# Run full analysis pipeline
analysis: data
	@echo "Running analysis..."
	python src/ems_readiness/analysis.py
	@echo "Analysis complete. Results saved to results/"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v

# Clean ALL generated files (data + results + caches)
clean:
	@echo "Cleaning all generated files..."
	rm -rf data/interim/*
	rm -rf data/processed/*.csv data/processed/*.parquet data/processed/*.geojson data/processed/*.json
	rm -rf data/processed/cache/
	rm -rf data/raw/*.pkl
	rm -rf data/manifests/*.csv
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
	touch data/interim/.gitkeep 2>/dev/null || true
	touch data/processed/.gitkeep 2>/dev/null || true
	touch results/figures/.gitkeep 2>/dev/null || true
	touch results/maps/.gitkeep 2>/dev/null || true
	touch results/tables/.gitkeep 2>/dev/null || true
	@echo "Clean complete."
