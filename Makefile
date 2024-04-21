test:
	python -m pytest -v

lint:
	- pylint nhltv_lib tests

format:
	black nhltv_lib tests --config black.toml

coverage:
	python -m pytest --cov=nhltv_lib --cov-report=term-missing --cov-report=html

type:
	mypy --disallow-untyped-calls nhltv_lib
