.PHONY: lint format typecheck test check-all

# Запуск лінтера
lint:
	ruff check.

# Запуск форматера
format:
	ruff format.

# Перевірка типів
typecheck:
	mypy.

# Запуск тестів
test:
	pytest tests/

# Комплексна перевірка коду всього життєвого циклу
check-all: format lint typecheck test
	@echo "=========================================="
	@echo "All quality checks passed successfully! ✨"
	@echo "=========================================="