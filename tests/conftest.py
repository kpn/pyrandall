import os

import vcr

defaults = ["method", "scheme", "host", "port", "path", "query"]
vcr = vcr.VCR(
    cassette_library_dir="tests/fixtures/vcr",
    # record_mode =  [once, new_episodes, none, all]
    # https://vcrpy.readthedocs.io/en/latest/usage.html#record-modes
    record_mode=os.environ.get("VCR_MODE", "once"),
    match_on=(defaults + ["body", "headers"]),
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
)
