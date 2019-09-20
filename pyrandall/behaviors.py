import json

import pyrandall


@pyrandall.hookimpl
def pyrandall_cli_banner(config):
    """
    Hook to overwrite banners printed at the
    start of pyrandall cli to stdout
    """
    return config


@pyrandall.hookimpl
def pyrandall_parse_http_request_template(filename, data):
    if filename.find(".json") > 0:
        body = json.dumps(json.loads(data))
        headers = {"content-type": "application/json"}
    else:
        body = data.encode()
        headers = {}

    return {"headers": headers, "body": body}


@pyrandall.hookimpl
def pyrandall_parse_broker_produce_template(filename, data):
    if ".json" in filename:
        output = json.dumps(json.loads(data))
    else:
        output = data

    return output.encode()


@pyrandall.hookimpl
def pyrandall_format_http_request_equals_to_event(filename, data):
    return json.dumps(json.loads(data)).encode()
