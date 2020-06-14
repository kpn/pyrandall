DOCKER_IMAGE=pyrandall
GIT_SHORT_SHA=$(git rev-parse --short HEAD)
GIT_REF_NAME=$(git rev-parse --abbrev-ref HEAD)

VERSION=$(<VERSION)
DOCKER_TAG="${DOCKER_IMAGE}:${VERSION}-${GIT_SHORT_SHA}"

if [ "$GIT_REF_NAME" = "master" ]
then
	# Tag existing as stable release (without git-short-sha)
	docker tag "${DOCKER_TAG}" "${DOCKER_IMAGE}:${VERSION}"
	docker tag "${DOCKER_TAG}" "${DOCKER_IMAGE}:master"
 # TODO: login and publish to dockerhub
else
  # Build new image and tag
	docker build -t "${DOCKER_TAG}" .
	docker tag "${DOCKER_TAG}" "${DOCKER_IMAGE}:latest"
 # TODO: login and publish to dockerhub
fi
