#!/bin/sh

set -x
./files/wait-for $KAFKA_BOOTSTRAP_SERVERS -t 30 -- tox
