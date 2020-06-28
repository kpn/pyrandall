import re


def test_empty_args_fails(pyrandall_cli):
    result = pyrandall_cli.invoke([])
    assert 'Usage: pyrandall' in result.output
    assert result.exit_code == 2

def test_cli_shows_version(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--version"
    ])
    assert result.exit_code == 0
    regex = r"pyrandall, version (\d+\.\d+\.\d+)\n$"
    matched = re.search(regex, result.output)
    assert matched

def test_missing_specfiles_arg(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--config",
        "examples/config/v1.json"
    ])
    assert 'Usage: pyrandall' in result.output
    assert "expecting at least one argument for specfiles" in result.output
    assert result.exit_code == 2

def test_too_much_specfiles_arg(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--config", "examples/config/v1.json",
        "examples/scenarios/one_event.yaml", "examples/scenarios/v2.yaml"
    ])
    assert 'Usage: pyrandall' in result.output
    assert 'passing multiple specfiles is not supported yet' in result.output
    assert result.exit_code == 2

def test_too_much_specfiles_arg(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--config", "examples/config/v1.json",
        "examples/scenarios/one_event.yaml", "examples/scenarios/v2.yaml"
    ])
    assert 'Usage: pyrandall' in result.output
    assert 'passing multiple specfiles is not supported yet' in result.output
    assert result.exit_code == 2

def test_fail_on_invaild_specfile_jsonschema(pyrandall_cli):
    result = pyrandall_cli.invoke([
        "--config",
        "examples/config/v1.json",
        "examples/scenarios/v2_ingest_kafka_invalid.yaml"
    ])
    expected_output = """Error on validating specfile examples/scenarios/v2_ingest_kafka_invalid.yaml with jsonschema, given error:
'messages' is a required property

Failed validating 'required' in schema['properties']['feature']['properties']['scenarios']['items']['properties']['simulate']['allOf'][0]['if']['then']:
    {'$id': '#/feature/properties/scenarios/items/properties/simulate/allOf/items/0/messages',
     'properties': {'messages': {'$ref': '#/definitions/simulateMessages'}},
     'required': ['messages']}

On instance['feature']['scenarios'][0]['simulate']:
    {'adapter': 'broker/kafka'}
"""

    assert expected_output == result.output
    assert result.exit_code == 4
