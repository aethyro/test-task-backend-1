PYTHON ?= python

.PHONY: run
run:
	uvicorn main:app --host 0.0.0.0 --port 8080

.PHONY: test
test:
	DB_DSN=sqlite://:memory: pytest -q

.PHONY: load-test
load-test:
	$(PYTHON) tests/load_test.py --base-url http://localhost:8080 --concurrency 20 --duration 15

.PHONY: locust
locust:
	locust -f tests/locustfile.py --host http://localhost:8080
