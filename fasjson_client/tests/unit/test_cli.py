import logging

import pytest
import click
from click.testing import CliRunner

from fasjson_client.cli import cli, log as logger, _register_subcommand


@pytest.fixture
def mocked_logging(mocker):
    yield mocker.patch("fasjson_client.cli.logging.basicConfig")


@pytest.fixture
def dummy_subcommand(mocker):
    @click.pass_obj
    def dummy(obj):
        click.echo(repr(obj))

    mocker.patch.object(cli, "commands", new={})
    cli.command()(dummy)


def test_cli_verbose(mocked_logging, dummy_subcommand):
    runner = CliRunner()
    result = runner.invoke(cli, ["--verbose", "dummy"])
    assert result.exit_code == 0
    mocked_logging.assert_called_with(format="%(message)s", level=logging.WARNING)
    assert logger.level == logging.DEBUG


def test_cli_quiet(mocked_logging, dummy_subcommand):
    runner = CliRunner()
    result = runner.invoke(cli, ["--quiet", "dummy"])
    assert result.exit_code == 0
    mocked_logging.assert_called_with(format="%(message)s", level=logging.WARNING)
    assert logger.level == logging.WARNING


def test_cli_verbose_and_quiet(mocked_logging, dummy_subcommand):
    runner = CliRunner()
    result = runner.invoke(cli, ["--verbose", "--quiet", "dummy"])
    assert result.exit_code == 2
    assert (
        "Error: You can't have --verbose and --quiet at the same time." in result.output
    )
    mocked_logging.assert_not_called()


def test_cli_url(mocked_logging, dummy_subcommand):
    runner = CliRunner()
    # Default URL
    result = runner.invoke(cli, ["dummy"])
    assert result.exit_code == 0
    assert result.output == "{'url': 'https://fasjson.os.fedoraproject.org'}\n"
    # Custom URL
    result = runner.invoke(cli, ["--url", "http://fasjson.example.com", "dummy"])
    assert result.exit_code == 0
    assert result.output == "{'url': 'http://fasjson.example.com'}\n"


def test_handle_import_error(mocked_logging, mocker):
    mocker.patch(
        "fasjson_client.cli.import_module",
        side_effect=ImportError("No module named 'dummy'"),
    )
    mocker.patch.object(cli, "commands", new={})
    _register_subcommand(cli, "dummy")
    runner = CliRunner()
    result = runner.invoke(cli, ["dummy"])
    assert result.exit_code == 1
    expected_msg = (
        "Error: This command needs additional dependencies: No module named 'dummy'\n"
    )
    assert result.output == expected_msg
