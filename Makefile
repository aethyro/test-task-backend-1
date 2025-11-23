.PHONY: run env

run: env
	@echo "Запуск приложения..."
	docker compose up

env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
	fi

test: env
	@echo "Запуск тестов..."
	python -m pytest tests

locust: env
	@echo "Запуск нагрузочного теста..."
	locust -f locustfile.py $(LOCUST_OPTS)
