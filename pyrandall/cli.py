import json
import sys
import os
import itertools
from argparse import ArgumentParser

import click
import jsonschema

from pyrandall import const
from pyrandall import commander
from pyrandall.hookspecs import get_plugin_manager
from pyrandall.spec import SpecBuilder
from pyrandall.types import Flags


@click.command(name="pyrandall")
@click.argument("specfiles", type=click.File('r'), nargs=-1)
@click.option("-c", "--config", 'config_file', type=click.File('r'), default="pyrandall_config.json", help="path to json file for pyrandall config.")
@click.option("-s", "--only-simulate", 'command_flag', flag_value=Flags.SIMULATE)
@click.option("-V", "--only-validate", 'command_flag', flag_value=Flags.VALIDATE)
@click.option("-e", "--everything", 'command_flag', flag_value=Flags.E2E, default=True)
@click.option("-d", "--dry-run", 'filter_flag', flag_value=Flags.DESCRIBE)
@click.help_option()
def main(config_file, command_flag, filter_flag, specfiles):
    """
    pyrandall a test framework oriented around data validation instead of code
    """
    # quickfix: Click will bypass argument callback when nargs=-1
    # raising these click exceptions will translate to exit(2)
    if not specfiles:
        raise click.BadParameter('expecting at least one argument for specfiles')

    if len(specfiles) > 1:
        raise click.UsageError("passing multiple specfiles is not supported yet")

    config = {}
    if config_file:
        config = json.load(config_file)


    # translate None to NO OP Flag
    if filter_flag is None:
        filter_flag = Flags.NOOP
    flags = command_flag | filter_flag

    try:
        run_command(config, flags, specfiles[0])
    except jsonschema.exceptions.ValidationError:
        print("Failed validating input yaml")
        exit(4)


def run_command(config, flags, specfile):
    # TODO: add logging options
    # with open("logging.yaml") as log_conf_file:
    #     log_conf = yaml.safe_load(log_conf_file)
    #     dictConfig(log_conf)

    config["default_request_url"] = config["requests"].pop("url")
    config['dataflow_path'] = build_basedir(specfile)
    config['specfile'] = specfile
    config['flags'] = flags

    # register plugins and call their initialize
    plugin_manager = get_plugin_manager()
    plugin_manager.hook.pyrandall_initialize(config=config)

    spec = SpecBuilder(hook=plugin_manager.hook, **config).feature()
    # commander handles execution flow with specified data and config
    commander.Commander(spec, flags).invoke()


def build_basedir(specfile):
    parts = specfile.name.split('/')
    out = []
    for x in itertools.takewhile(lambda x: x != const.DIRNAME_SCENARIOS, parts):
        out.append(x)
    return os.path.abspath('/'.join(out))

if __name__ == "__main__":
    main()
