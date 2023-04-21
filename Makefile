PYTHON=venv/bin/python3

.DEFAULT:
	help

help:
	@echo "I don't know what you want me to do."

init:
	python3 -m venv venv
	${PYTHON} -m pip install -r dev_requirements.txt

download:
	${PYTHON} downloader.py

publish:
	${PYTHON} publisher.py

mypy:
	${PYTHON} -m mypy --ignore-missing-imports .

flake8:
	${PYTHON} -m flake8 .

black:
	${PYTHON} -m black .

test:
	${PYTHON} -m pytest

coverage:
	${PYTHON} -m coverage run -m pytest
	${PYTHON} -m coverage report -m

before-commit:
	make black
	make test
	make mypy
	make flake8

ipython:
	${PYTHON} -c "import IPython;IPython.terminal.ipapp.launch_new_instance();"