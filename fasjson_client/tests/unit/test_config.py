import os

import pytest
import toml

from fasjson_client.cli import cli
from fasjson_client.config import LazyConfig, DEFAULTS, VALIDATORS
from fasjson_client.errors import ConfigurationException


@pytest.fixture
def conf():
    conf = LazyConfig("dummy-app", DEFAULTS, VALIDATORS)
    conf._load_paths = []
    return conf


@pytest.fixture
def config_env_var(tmpdir):
    config_path = os.path.join(tmpdir, "config.toml")
    open(config_path, "w").close()
    os.environ["DUMMY_APP_CONF"] = config_path
    yield config_path
    del os.environ["DUMMY_APP_CONF"]


def test_config_dict_behavior(mocker, conf):
    for key, value in DEFAULTS.items():
        assert conf[key] == value
        assert conf.get(key) == value
    assert len(conf) == len(DEFAULTS)
    assert list(conf) == list(DEFAULTS)
    # assert conf.copy() == DEFAULTS.copy()
    conf.update({"foo": "bar"})
    assert conf["foo"] == "bar"


def test_config_iter_behavior(mocker, conf):
    load_config = mocker.spy(conf, "load_config")

    iterator = iter(conf)
    assert "url" in iterator
    assert load_config.call_count == 1

    # Verify that the configuration is cached
    iterator = iter(conf)
    assert "verbose" in iterator
    assert load_config.call_count == 1


def test_config_lazy_load(mocker, conf):
    load_config = mocker.spy(conf, "load_config")
    key = list(DEFAULTS)[0]

    conf.reset()
    conf[key]
    conf[key]
    assert load_config.call_count == 1

    conf.reset()
    conf.get(key)
    conf.get(key)
    assert load_config.call_count == 2

    conf.reset()
    len(conf)
    len(conf)
    assert load_config.call_count == 3

    conf.reset()
    list(conf)
    list(conf)
    assert load_config.call_count == 4

    conf.reset()
    conf.update({"foo": "bar"})
    conf.update({"foo": "bar"})
    assert load_config.call_count == 5


def test_config_no_pop(conf):
    key = list(DEFAULTS)[0]
    with pytest.raises(ConfigurationException):
        conf.pop(key)


def test_config_unknown_value(conf):
    conf["foo"] = "bar"
    with pytest.raises(ConfigurationException):
        conf._validate()


def test_config_load_paths(conf, mocker, tmpdir):
    toml_load = mocker.spy(toml, "load")
    validate_method = mocker.patch.object(conf, "_validate")
    conf._load_paths = [
        os.path.join(tmpdir, "first.toml"),
        os.path.join(tmpdir, "second.toml"),
        os.path.join(tmpdir, "third.toml"),
    ]
    # Only create the first two
    with open(os.path.join(tmpdir, "first.toml"), "w") as f:
        f.write("foo = 'bar1'")
    with open(os.path.join(tmpdir, "second.toml"), "w") as f:
        f.write("foo = 'bar2'")

    conf.load_config()

    loaded = [call[0][0] for call in toml_load.call_args_list]
    assert loaded == conf._load_paths[0:2]
    validate_method.assert_called_with()
    # Make sure the last value prevailed
    assert conf["foo"] == "bar2"


def test_config_load_one(conf, mocker, tmpdir):
    toml = mocker.patch("fasjson_client.config.toml")
    toml.load.return_value = {"foo": "bar"}
    validate_method = mocker.patch.object(conf, "_validate")
    config_path = os.path.join(tmpdir, "config.toml")
    open(config_path, "w").close()

    conf.load_config(config_path)

    toml.load.assert_called_once_with(config_path)
    validate_method.assert_called_with()
    assert conf["foo"] == "bar"


def test_config_load_env(conf, mocker, config_env_var):
    toml = mocker.patch("fasjson_client.config.toml")
    toml.load.return_value = {}
    validate_method = mocker.patch.object(conf, "_validate")

    conf.load_config()

    toml.load.assert_called_once_with(config_env_var)
    validate_method.assert_called_with()


def test_config_load_one_does_not_exist(conf, mocker, tmpdir):
    toml = mocker.patch("fasjson_client.config.toml")
    validate_method = mocker.patch.object(conf, "_validate")
    config_path = os.path.join(tmpdir, "config.toml")
    # Don't create the file

    with pytest.raises(ConfigurationException) as e:
        conf.load_config(config_path)
    expected_msg = "the specified configuration file {} does not exist.".format(
        config_path
    )
    assert e.value.message == expected_msg

    toml.load.assert_not_called()
    validate_method.assert_not_called()


def test_config_load_one_invalid(conf, mocker, tmpdir):
    config_path = os.path.join(tmpdir, "config.toml")
    with open(config_path, "w") as f:
        f.write("invalid")

    with pytest.raises(ConfigurationException) as e:
        conf.load_config(config_path)
    expected_msg = (
        "Failed to parse {}: error at line 1, column 8: Key name found without value. "
        "Reached end of file."
    ).format(config_path)
    assert e.value.message == expected_msg


def test_config_error():
    e = ConfigurationException("foo")
    assert str(e) == "Configuration error: foo"


# Tests below are specific to fasjson-client


def test_config_for_each_cli_option(conf):
    """Make sure all cli options have fallbacks in the configuration file"""
    for param in cli.params:
        if param.name == "config_path":
            continue  # This is the only one not in the configuration
        assert (
            param.name in DEFAULTS
        ), "Parameter {} is not in the configuration".format(param.name)
    for subcommand_name in cli.list_commands(None):
        subcommand = cli.get_command(None, subcommand_name)
        for param in subcommand.params:
            assert (
                param.name in DEFAULTS[subcommand_name]
            ), "Parameter {} is not in the configuration for command {}".format(
                param.name, subcommand_name
            )


def test_config_invalid_url(conf, tmpdir):
    config_path = os.path.join(tmpdir, "config.toml")
    with open(config_path, "w") as f:
        f.write("url = 'invalid'")
    with pytest.raises(ConfigurationException) as e:
        conf.load_config(config_path)
    assert e.value.message == "the url value must start with http:// or https://."
