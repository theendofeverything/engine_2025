run:
	./__main__.py

lint:
	-pycodestyle --max-line-length=100 .
	-pylint .
	-mypy --strict .
	-flake8 --max-complexity 10 --max-line-length 100 --extend-ignore F821
