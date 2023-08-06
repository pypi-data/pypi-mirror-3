init:
	pip install -r requirements.txt

server:
	pip install -r requirements-server.txt

dev:
	pip install -r requirements-test.txt
	pip install -r requirements-docs.txt

test:
	tox

functional-test:
	tox -e func

html:
	pip install -r requirements-docs.txt
	cd docs; $(MAKE) html
