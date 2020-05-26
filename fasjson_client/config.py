"""
fasjson-client can be configured with configuration files that are loaded in the following order:

1. ``/etc/fasjson-client/config.toml``
2. ``~/.config/fasjson-client/config.toml``
3. ``./config.toml``

Values found in later configuration files overwrite values found in earlier files.

If a configuration is explicitely chosen, or if the ``FASJSON_CLIENT_CONF`` environment variable is
set, only the selected file is loaded.

Values given on the command-line overwrite values in the configuration file(s).

Each configuration option has a default value.

.. contents:: Table of Configuration Options :local:

A complete example TOML configuration:

.. literalinclude:: ../config.toml.example

"""

import copy
import logging
import os
from collections.abc import MutableMapping

import toml

from .errors import ConfigurationException


_log = logging.getLogger(__name__)

#: The default configuration settings for fasjson-client. This should not be
#: modified and should be copied with :func:`copy.deepcopy`.
DEFAULTS = {
    "url": "https://fasjson.os.fedoraproject.org",
    "verbose": False,
    "quiet": False,
    "get-cert": {
        "username": None,
        "existing": False,
        "private_key": None,
        "save_to": None,
        "overwrite": False,
    },
}


def _validate_url(value):
    if not value.startswith("http://") and not value.startswith("https://"):
        raise ConfigurationException(
            "the url value must start with http:// or https://."
        )


VALIDATORS = {
    "url": _validate_url,
}


class LazyConfig(MutableMapping):
    """This class lazy-loads the configuration file."""

    def __init__(self, app_name, defaults=None, validators=None):
        self._data = dict()
        self._app_name = app_name
        self._defaults = defaults
        self._validators = validators
        self._env_var = "{}_CONF".format(self._app_name.replace("-", "_").upper())
        self.loaded = False
        self._load_paths = [
            "/etc/{}/config.toml".format(self._app_name),
            os.path.expanduser("~/.config/{}/config.toml".format(self._app_name)),
            os.path.join(os.getcwd(), "config.toml"),
        ]

    def __getitem__(self, key):
        if not self.loaded:
            self.load_config()
        return self._data.__getitem__(key)

    def __setitem__(self, key, value):
        if not self.loaded:
            self.load_config()
        return self._data.__setitem__(key, value)

    def __delitem__(self, key):
        raise ConfigurationException("Configuration keys cannot be removed!")

    def __iter__(self):
        if not self.loaded:
            self.load_config()
        return self._data.__iter__()

    def __len__(self):
        if not self.loaded:
            self.load_config()
        return self._data.__len__()

    def _validate(self):
        """Perform checks on the configuration to assert its validity.

        Raises:
            ConfigurationException: If the configuration is invalid.
        """
        for key in self:
            if key not in self._defaults:
                raise ConfigurationException(
                    'Unknown configuration key "{}"! Valid configuration keys are'
                    " {}".format(key, list(self._defaults.keys()))
                )
            if key in self._validators:
                self._validators[key](self[key])

    def load_config(self, config_path=None):
        """Load application configuration from a file and merge it with the default configuration.

        If the appripriate environment variable is set to a filesystem path, the configuration will
        be loaded from that location.
        """
        self.loaded = True
        config = copy.deepcopy(self._defaults)

        if config_path is None and self._env_var in os.environ:
            config_path = os.environ[self._env_var]

        if config_path is None:
            config_paths = self._load_paths
        elif not os.path.exists(config_path):
            raise ConfigurationException(
                "the specified configuration file {} does not exist.".format(
                    config_path
                )
            )
        else:
            config_paths = [config_path]

        for config_path in config_paths:
            if not os.path.exists(config_path):
                continue
            _log.info("Loading configuration from {}".format(config_path))
            try:
                file_config = toml.load(config_path)
                for key in file_config:
                    config[key.lower()] = file_config[key]
            except toml.TomlDecodeError as e:
                msg = "Failed to parse {}: error at line {}, column {}: {}".format(
                    config_path, e.lineno, e.colno, e.msg
                )
                raise ConfigurationException(msg)

        self.update(config)
        self._validate()
        return self

    def reset(self):
        self.loaded = False
        self._data = dict()


#: The configuration dictionary used by fasjson_client.
conf = LazyConfig("fasjson-client", DEFAULTS, VALIDATORS)
