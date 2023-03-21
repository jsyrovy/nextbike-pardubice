PYTHON=venv/bin/python3

.DEFAULT:
	help

help:
	@echo "I don't know what you want me to do."

init:
	python3 -m venv venv
	${PYTHON} -m pip install -r publisher_requirements.txt
	${PYTHON} -m pip install -r test_requirements.txt

download:
	${PYTHON} downloader.py

publish:
	${PYTHON} publisher.py

black:
	${PYTHON} -m black .
