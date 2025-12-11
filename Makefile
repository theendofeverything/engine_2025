run:
	./__main__.py

lint:
	-pycodestyle --max-line-length=100 .
	-pylint .
	# -mypy .
	-flake8 --max-complexity 5 --max-line-length 100 .
