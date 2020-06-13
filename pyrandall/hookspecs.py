import sys

import pluggy

import pyrandall

hookspec = pluggy.HookspecMarker("pyrandall")
# should be imported via pyrandall API (see pyrandall/__init__.py)
_hookimpl = pluggy.HookimplMarker("pyrandall")


def get_plugin_manager(plugins=()):
    pm = pluggy.PluginManager("pyrandall")
    # add default implementations
    pm.add_hookspecs(sys.modules[__name__])
    pm.register(pyrandall.behaviors)
    pm.load_setuptools_entrypoints("pyrandallX")
    pm.check_pending()
    return pm


@hookspec(firstresult=True)
def pyrandall_cli_banner(config):
    """
    Hook to overwrite banners printed at the
    start of pyrandall cli to stdout
    """


@hookspec
def pyrandall_initialize(config):
    """
    Initialize hook for plugins
    called in startup of pyrandall with config
    :return: None
    """


@hookspec(firstresult=True)
def pyrandall_parse_http_request_template(filename, data):
    """
    Pyrandall scenario's can simulate events over http.
    Template files are read from `${dataflow}/events/`.

    Here you can implement your own template format or parsing
    of the file.

    Output dict may contain 'headers', 'method' and 'body'
    The url and path are configured via the yaml spec.

    :return: dict
    """


@hookspec(firstresult=True)
def pyrandall_parse_broker_produce_template(filename, data):
    """
    Pyrandall scenario's can simulate events over broker (kafka etc)
    Template files are read from `${dataflow}/events/`.

    Here you can implement your own template format or parsing
    of the file.

    Output dict may contain keys 'value', 'headers',
    'key' and 'headers'

    :return: dict
    """


@hookspec(firstresult=True)
def pyrandall_format_http_request_equals_to_event(filename, data):
    """
    return value will be asserted as expected value
    against the body of a HTTP response as defined in the yaml spec

    called upon both the requests/http adapter

    :return: bytes
    """


@hookspec(firstresult=True)
def pyrandall_format_kafka_equals_to_event(filename, data):
    """
    return value will be asserted as expected value
    against the consumed message from kafka as defined in the yaml spec

    called upon the broker/kafka adapter

    :return: bytes
    """
