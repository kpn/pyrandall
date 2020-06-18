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


@click.group()
@click.pass_context
@click.option("--config", type=click.File('r'), default="pyrandall_config.json", help="path to json file for pyrandall config.")
def main(ctx, config):
    """
    pyrandall a test framework oriented around data validation instead of code
    """
    ctx.obj = {}
    if config:
        ctx.obj.update(json.load(config))


@main.command()
@click.pass_context
@click.argument("specfiles", type=click.File('r'), nargs=-1)
def simulate(ctx, specfiles):
    """
    run Simulator for specfiles
    """
    ctx.obj['flags'] = Flags.SIMULATE
    start(specfiles, ctx.obj)


@main.command()
@click.pass_context
@click.argument("specfiles", type=click.File('r'), nargs=-1)
def validate(ctx, specfiles):
    """
    run Validate for specfiles
    """
    ctx.obj['flags'] = Flags.VALIDATE
    start(specfiles, ctx.obj)


def start(specfiles: tuple, config: dict):
    if len(specfiles) > 1:
        raise NotImplemented("Passing multiple paths is not supported yet")
    config['specfile'] = specfiles[0]
    try:
        run_command(config)
    except jsonschema.exceptions.ValidationError:
        print("Failed validating input yaml")
        exit(4)


def run_command(config):
    # TODO: add logging options
    # with open("logging.yaml") as log_conf_file:
    #     log_conf = yaml.safe_load(log_conf_file)
    #     dictConfig(log_conf)

    config["default_request_url"] = config["requests"].pop("url")
    config['dataflow_path'] = build_basedir(config['specfile'])

    # register plugins and call their initialize
    plugin_manager = get_plugin_manager()
    plugin_manager.hook.pyrandall_initialize(config=config)

    spec = SpecBuilder(hook=plugin_manager.hook, **config).feature()
    # commander handles execution flow with specified data and config
    commander.Commander(spec, config["flags"]).invoke()


def build_basedir(specfile):
    parts = specfile.name.split('/')
    out = []
    for x in itertools.takewhile(lambda x: x != const.DIRNAME_SCENARIOS, parts):
        out.append(x)
    return os.path.abspath('/'.join(out))


if __name__ == "__main__":
    main()
