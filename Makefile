run:
	./main.py

tests:
	pytest --doctest-modules --verbose --maxfail=1

lint:
	-pycodestyle .
	-pylint .
	-mypy --strict .
	-flake8 .
