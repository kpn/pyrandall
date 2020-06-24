from os import path

DIRNAME_SCENARIOS = "scenarios"
DIRNAME_EVENTS = "events"
DIRNAME_RESULTS = "results"

DIR_PYRANDALL_HOME = path.dirname(path.abspath(__file__))

# Constants to resolve private schema files
_v2_path = path.join("files", "schemas", "scenario", "v2.yaml")
SCHEMA_V2_PATH = path.join(DIR_PYRANDALL_HOME,  _v2_path)
VERSION_SCENARIO_V2 = "scenario/v2"
SCHEMA_VERSIONS = [VERSION_SCENARIO_V2]

# Package version
_version_path = path.join("files", "VERSION")
VERSION_PATH = path.join(DIR_PYRANDALL_HOME, _version_path)
