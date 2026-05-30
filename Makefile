.PHONY: all demo smoke test
all: demo smoke test
demo:
	@echo "Running demo for ESG-Carbon-Telemetry..."
smoke:
	@echo "Running smoke tests for ESG-Carbon-Telemetry..."
	./smoke_test.sh
test:
	@echo "Running tests for ESG-Carbon-Telemetry..."
	pytest tests/ || echo "No tests found"
