"""Shared loader for publish/dataset.yaml.

Usage as a module: ``cfg = load(path)``; as a script: ``python config.py dataset.yaml <key>``
prints one value (used by the Makefile). Path-valued keys are resolved to absolute paths.
"""
import os
import sys

import yaml

PATH_KEYS = ("source_dir", "staging_dir", "assets_dir")


def load(path: str) -> dict:
    path = os.path.abspath(path)
    with open(path) as f:
        cfg = yaml.safe_load(f)
    base = os.path.dirname(path)
    for key in PATH_KEYS:
        if key in cfg:
            cfg[key] = os.path.abspath(os.path.join(base, os.path.expanduser(cfg[key])))
    cfg["_config_dir"] = base
    return cfg


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: config.py <dataset.yaml> <key>")
    print(load(sys.argv[1])[sys.argv[2]])
