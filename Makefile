test:
	python -m pytest -v

lint:
	- python -m flake8 nhltv_lib/ tests/

format:
	black nhltv_lib tests

coverage:
	python -m pytest --cov=nhltv_lib --cov-report=term-missing --cov-report=html
