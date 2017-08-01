init:
	pip install -r requirements.txt
	python setup.py develop

test:
	python -m unittest discover
