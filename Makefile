run:
	./main.py

tests:
	pytest --doctest-modules --verbose --maxfail=1

lint:
	-pycodestyle --max-line-length=100 .
	-pylint .
	-mypy --strict .
	-flake8 --max-complexity 10 --max-line-length 100 --extend-ignore F821 .
