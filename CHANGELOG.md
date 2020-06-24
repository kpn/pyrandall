# Changelog
All notable changes to pyrandall will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2020-06-24
### Changed
- *BREAKING CHNAGES*:
Pyrandall is moving to single command cli. Similar to pytest and rspec.
### Removed
- the cli sub-commands `simulate`, `sanitycheck` and `validate`
in favor of a single command with options flags.
- the option for `--dataflow` in favor of absolute paths to a scenario file.
the event/result files mentioned in a specfile are resolved by relative lookup
still trying to adhere to "convention over configuration".
In future release support for directory wildcards can be added without breaking the api.
### Added
- added option `--everything` (to run e2e) that is the default. Meaning will run both simulate and validate steps from the spec.
The execution order (sync or async) is open for extension.
This should be treated as an alpha feature followed by fixes and enhancements.


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
