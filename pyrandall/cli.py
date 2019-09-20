import json
import sys
from argparse import ArgumentParser

import jsonschema

from pyrandall import commander
from pyrandall.hookspecs import get_plugin_manager
from pyrandall.spec import SpecBuilder
from pyrandall.types import Flags

FLAGS_MAP = {
    "simulate": Flags.SIMULATE,
    "validate": Flags.VALIDATE,
    "sanitytest": Flags.VALIDATE,  # legacy command
}


def run_command(config):
    # remove unwanted keys and pass config as keyword arguments
    del config["func"]
    specfile = config.pop("specfile")
    config["default_request_url"] = config["requests"].pop("url")

    # register plugins and call their initialize
    plugin_manager = get_plugin_manager()
    plugin_manager.hook.pyrandall_initialize(config=config)

    spec = SpecBuilder(specfile, hook=plugin_manager.hook, **config).feature()
    flags = FLAGS_MAP[config["command"]]
    # commander handles execution flow with specified data and config
    commander.Commander(spec, flags).invoke()


def add_common_args(parser):
    parser.add_argument("specfile", type=str, help="name of yaml file in scenario/")


def setup_args():
    parser = ArgumentParser(
        description="pyrandall a test framework oriented around data validation instead of code"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="pyrandall_config.json",
        dest="config_path",
        help="path to json file for pyrandall config.",
    )
    parser.add_argument(
        "--dataflow",
        type=str,
        required=True,
        dest="dataflow_path",
        help="path to dataflow root directory",
    )

    subparsers = parser.add_subparsers(dest="command")
    # add simulate subcommand
    sim_parser = subparsers.add_parser("simulate", help="run Simulator for specfile")
    sim_parser.set_defaults(func=run_command)
    add_common_args(sim_parser)
    # add sanitycheck (legacy name)
    san_parser = subparsers.add_parser(
        "sanitytest", help="run Validate for specfile (Use validate command)"
    )
    san_parser.set_defaults(func=run_command)
    add_common_args(san_parser)
    # add validate subcommand
    val_parser = subparsers.add_parser("validate", help="run Validate for specfile")
    val_parser.set_defaults(func=run_command)
    add_common_args(val_parser)

    return parser


def argparse_error(args_data):
    msg = """
#######
Exit code was 2! Its assumed mocked arguments are wrong, see argparse usage below:

\t%s

actual arguments passed to mock:
\t%s

######
""" % (
        setup_args().format_help().replace("\n", "\n\t"),
        args_data,
    )
    return msg


def load_config(fpath):
    with open(fpath, "r") as f:
        return json.load(f)


def start(argv, config=None):
    parser = setup_args()
    args_config = parser.parse_args(argv)

    # TODO: add logging options
    # with open("logging.yaml") as log_conf_file:
    #     log_conf = yaml.safe_load(log_conf_file)
    #     dictConfig(log_conf)

    if args_config.command is None:
        parser.error("not a valid pyrandall command")
        exit(1)

    if config is None:
        config = load_config(args_config.config_path)

    # overwrite with cli options
    config.update(args_config.__dict__)

    try:
        args_config.func(config)
    except jsonschema.exceptions.ValidationError:
        print("Failed validating input yaml")
        exit(4)
    exit(0)


def main():
    start(sys.argv[1:])


if __name__ == "__main__":
    main()
