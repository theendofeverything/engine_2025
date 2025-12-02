run:
	./__main__.py

lint:
	-pycodestyle .
	-pylint .
	-mypy .
	-flake8 --max-complexity 5 .
