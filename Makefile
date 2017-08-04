init:
	pip install -r requirements.txt
	pip uninstall sparse
	pip install https://github.com/ljdursi/sparse.git
	python setup.py develop

test:
	python -m unittest discover
