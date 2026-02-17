run:
	./main.py

tests:
	pytest --doctest-modules --verbose --maxfail=1

lint:
	-pylint .
	-mypy --strict .
	-flake8 .
