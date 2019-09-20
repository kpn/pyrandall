VERSION=$(shell cat VERSION)

.PHONY: ctags
ctags:
	ctags -R --exclude=.tox --exclude=venv --python-kinds=-i pyrandall tests


.PHONY: pyrandall
pyrandall:
	tox
	docker build -t pyrandall:${VERSION} .
	docker tag pyrandall:${VERSION} pyrandall:latest
