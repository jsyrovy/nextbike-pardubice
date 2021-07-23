PYTHON=venv/bin/python3

.DEFAULT:
	help

help:
	@echo "make help"
	@echo "  show help"
	@echo "make init"
	@echo "  create venv and install requirements"
	@echo "make download"
	@echo "  run downloader"
	@echo "make publish"
	@echo "  run publisher"

init:
	python3 -m venv venv
	${PYTHON} -m pip install -r publisher_requirements.txt
	${PYTHON} -m pip install -r test_requirements.txt

download:
	${PYTHON} downloader.py

publish:
	${PYTHON} publisher.py
