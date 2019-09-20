FROM python:3.6-alpine3.9 as builder

COPY . work
WORKDIR /work

RUN echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
  apk update && apk upgrade && \
  apk add --no-cache --virtual build-dependencies build-base && \
  apk add --no-cache librdkafka-dev@edge~=1.1.0 && \
		pip install --install-option="--prefix=/install" . && \
  apk del build-dependencies

FROM python:3.6-alpine3.9


ENV HOME=/home/pyrandall

RUN echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories && \
    apk update && apk upgrade && \
    apk add --no-cache librdkafka@edge~=1.1.0 && \
    apk add ca-certificates && rm -rf /var/cache/apk/* && \
    addgroup -S -g 1000 pyrandall && \
    adduser -D -S -u 1000 -G pyrandall -h $HOME pyrandall

COPY --from=builder /install /usr/local/
RUN update-ca-certificates

WORKDIR /home/pyrandall
USER pyrandall
COPY logging.yaml .

ENTRYPOINT ["pyrandall"]
