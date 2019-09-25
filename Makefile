DOCKER_COMPOSE=$(shell which docker-compose)
VERSION=$(shell cat VERSION)

.PHONY: ctags
ctags:
	ctags -R --exclude=.tox --exclude=venv --python-kinds=-i pyrandall tests


.PHONY: pyrandall
pyrandall:
	tox
	docker build -t pyrandall:${VERSION} .
	docker tag pyrandall:${VERSION} pyrandall:latest

.PHONY:
tox:
	tox -e py36,fix-lint

.PHONY: travis-pr-build
travis-pr-build:
		$(DOCKER_COMPOSE) build tox

.PHONY: travis-pr-test
travis-pr-test:
	$(DOCKER_COMPOSE) run --rm tox -e py36,fix-lint
