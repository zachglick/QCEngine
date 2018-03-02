"""
Creates globals for the dqm_compute module
"""

import os
import socket
import fnmatch
import yaml
import json

__all__ = ["get_config"]

# Start a globals dictionary with small starting values
_globals = {}

_globals["hostname"] = socket.gethostname()
_globals["default_compute"] = {
    "psi_path": None,
    "jobs_per_node": 1,
    "cores_per_job": 1,
    "memory_per_job": 2
}
_globals["other_compute"] = {}


def _load_locals():

    # Find the dqm_config
    load_path = None
    test_paths = [os.getcwd(), os.path.join(os.path.expanduser('~'), ".dqm")]

    if "FW_CONFIG_FILE" in os.environ:
        test_paths.insert(0, "FW_CONFIG_FILE")

    for path in test_paths:
        path = os.path.join(path, "dqm_config.yaml")
        if os.path.exists(path):
            load_path = path
            break

    if load_path is None:
        raise OSError("Could not find 'dqm_config.yaml'. Search the following paths: %s" %
                      ", ".join(test_paths))

    # Load the library
    with open(load_path) as stream:
        user_config = yaml.load(stream)

    # Override default keys
    default_keys = list(_globals["default_compute"].keys())

    if "default_compute" in user_config:
        for k, v in user_config["default_compute"].items():
            if k not in default_keys:
                raise KeyError("Key %s not accepted for default_compute" % k)
            _globals["default_compute"][k] = v

    default_keys.append("hostname")

    if "other_compute" in user_config:
        for host, config in user_config["other_compute"].items():
            _globals["other_compute"][host] = _globals["default_compute"].copy()

            if "hostname" not in config:
                raise KeyError("Other_compute must have a hostname to help identify the server")
            for k, v in config.items():
                if k not in default_keys:
                    raise KeyError("Key %s not accepted for default_compute" % k)
                _globals["other_compute"][host][k] = v

# Pull in the local variables
_load_locals()


def get_config(key=None, hostname=None):
    """
    Returns the configuration key for dqm_compute.
    """
    config = None
    if hostname is None:
        config = _globals["default_compute"]
    else:

        # Find a match
        for host, config in _globals["other_compute"].items():
            if fnmatch.fnmatch(hostname, config["hostname"]):
                hostname = host
                config = config
                break

        # Use default
        if hostname is None:
            config = _globals["default_compute"]

    if key is None:
        return config.copy()
    else:
        if key not in config:
            raise Exception("Key %s asked for, but not in local data")
        return config[key]
