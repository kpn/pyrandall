# Changelog
All notable changes to pyrandall will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2020-05-13
### Fixed
- Implemented `assert_that_received` in kafka validate spec.
  And `assert_that_empty` in kafka validate spec.
  See `examples/scenarios/v2_ingest_kafka_small.yaml`


## [0.1.0] - 2019-09-20
### Added
- Initial commit after code inspection was performed at KPN
- a README.md explaining the project
- LICENCE file with Apache Licence 2.0
- All unit and functional tests with pytest under tests/
- a tox.ini to automate virtualenv creation and running tests
- a Dockerfile that exposes main API to users
- examples/ show example usage
