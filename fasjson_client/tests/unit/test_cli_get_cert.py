import os

import pytest
from cryptography.hazmat.primitives import serialization
from click.testing import CliRunner

from fasjson_client import Client
from fasjson_client.cli import cli
from fasjson_client.errors import ClientError


@pytest.fixture
def invoker():
    runner = CliRunner()

    def invoke(*args):
        return runner.invoke(
            cli, ["--url", "http://example.com/fasjson", "get-cert"] + list(args)
        )

    return invoke


@pytest.fixture
def get_cert_b64(fixture_dir):
    def _get_cert(idx):
        with open(os.path.join(fixture_dir, "cert-{}.crt".format(idx)), "r") as f:
            return "".join(f.read().splitlines()[1:-1])

    return _get_cert


def test_no_save_to(invoker, mocker):
    result = invoker()
    assert result.exit_code == 2
    expected_msg = (
        "Error: Invalid value for save_to: the destination file must be specified "
        "on the command line or in the configuration file."
    )
    assert expected_msg in result.output


def test_no_private_key(invoker):
    result = invoker("-u", "dummy", "--save-to", "dummy")
    assert result.exit_code == 2
    expected_msg = (
        "Error: if you want a new certificate, you need to provide a path "
        "for the private key to be loaded from or saved to.\n"
    )
    assert expected_msg in result.output


def test_no_username(invoker, mocker):
    mocker.patch("fasjson_client.cli.get_cert.getuser", side_effect=KeyError)
    result = invoker("--save-to", "dummy", "--existing")
    assert result.exit_code == 2
    expected_msg = "Error: Invalid value for username: you must provide a username."
    assert expected_msg in result.output


def test_existing_destination_exists(invoker, tmp_path):
    dest_file = os.path.join(tmp_path, "dummy")
    open(dest_file, "w").close()
    result = invoker("--existing", "-u", "dummy", "--save-to", dest_file)
    assert result.exit_code == 2
    expected_msg = (
        "Error: Invalid value for save_to: the destination file "
        "{} already exists. Aborting.\n".format(dest_file)
    )
    assert expected_msg in result.output


def test_existing(invoker, server, tmp_path, get_cert_b64, fixture_dir):
    dest_file = os.path.join(tmp_path, "dummy")
    user_response = {
        # Reverse the list to make sure the certs are sorted.
        "result": {
            "certificates": list(reversed([get_cert_b64(idx) for idx in range(1, 5)]))
        }
    }
    server.mock_endpoint("/users/dummy/", json=user_response)

    result = invoker("--existing", "-u", "dummy", "--save-to", dest_file)
    assert result.exit_code == 0

    with open(dest_file, "r") as f:
        result_cert = f.read()
    with open(os.path.join(fixture_dir, "cert-4.crt"), "r") as f:
        expected_cert = f.read()
    assert result_cert == expected_cert


def test_existing_no_cert(invoker, server, tmp_path):
    dest_file = os.path.join(tmp_path, "dummy")
    user_response = {"result": {"certificates": []}}
    server.mock_endpoint("/users/dummy/", json=user_response)

    result = invoker("--existing", "-u", "dummy", "--save-to", dest_file)
    assert result.exit_code == 1
    expected_msg = "Error: No existing certificate, you need to request one.\n"
    assert result.output == expected_msg
    assert not os.path.exists(dest_file)


def test_existing_no_user(invoker, server, tmp_path):
    dest_file = os.path.join(tmp_path, "dummy")
    server.mock_endpoint("/users/dummy/", status_code=404, reason="Not Found")

    result = invoker("--existing", "--save-to", dest_file, "-u", "dummy")
    assert result.exit_code == 1
    expected_msg = "Error: user dummy not found.\n"
    assert result.output == expected_msg
    assert not os.path.exists(dest_file)


def test_existing_api_error(invoker, server, tmp_path):
    dest_file = os.path.join(tmp_path, "dummy")
    server.mock_endpoint("/users/dummy/", status_code=500, reason="Server Error")

    result = invoker("--existing", "--save-to", dest_file, "-u", "dummy")
    assert result.exit_code == 1
    expected_msg = "Error: 500 Server Error\n"
    assert result.output == expected_msg
    assert not os.path.exists(dest_file)


def test_existing_client_error(invoker, mocker, tmp_path):
    dest_file = os.path.join(tmp_path, "dummy")
    mocker.patch.object(
        Client,
        "_make_bravado_client",
        side_effect=ClientError(message="dummy error", code=42),
    )
    result = invoker("--existing", "-u", "dummy", "--save-to", dest_file)
    assert result.exit_code == 1
    expected_msg = "Error: could not get existing certificate (dummy error).\n"
    assert result.output == expected_msg
    assert not os.path.exists(dest_file)


def test_sign_make_pkey(invoker, server, tmp_path, get_cert_b64, fixture_dir):
    dest_cert = os.path.join(tmp_path, "dummy.crt")
    dest_key = os.path.join(tmp_path, "dummy.key")
    user_response = {"result": {"certificate": get_cert_b64(1)}}
    server.mock_endpoint("/certs/", method="POST", json=user_response)

    result = invoker("-u", "dummy", "--save-to", dest_cert, "--private-key", dest_key)
    assert result.exit_code == 0

    # Check private key
    assert os.path.exists(dest_key)
    with open(dest_key, "r") as f:
        result_key = f.read()
    assert result_key.splitlines()[0] == "-----BEGIN RSA PRIVATE KEY-----"

    # Check cert
    with open(dest_cert, "r") as f:
        result_cert = f.read()
    with open(os.path.join(fixture_dir, "cert-1.crt"), "r") as f:
        expected_cert = f.read()
    assert result_cert == expected_cert


def test_sign_make_pkey_failure(invoker, server, tmp_path, get_cert_b64, fixture_dir):
    dest_cert = os.path.join(tmp_path, "dummy.crt")
    dest_key = os.path.join(tmp_path, "sub-directory", "dummy.key")
    user_response = {"result": {"certificate": get_cert_b64(1)}}
    server.mock_endpoint("/certs/", method="POST", json=user_response)

    result = invoker("-u", "dummy", "--save-to", dest_cert, "--private-key", dest_key)
    assert result.exit_code == 1
    assert (
        result.output == "Error: can't make a private key: No such file or directory\n"
    )


def test_sign_error(invoker, server, tmp_path, get_cert_b64, fixture_dir):
    dest_cert = os.path.join(tmp_path, "dummy.crt")
    dest_key = os.path.join(tmp_path, "dummy.key")
    server.mock_endpoint(
        "/certs/",
        method="POST",
        status_code=500,
        # reason="Dummy Error",
        json={"message": "dummy error"},
    )

    result = invoker("-u", "dummy", "--save-to", dest_cert, "--private-key", dest_key)
    assert result.exit_code == 1
    expected_msg = "Error: could not sign the CSR (500: dummy error, {'message': 'dummy error'}).\n"
    assert result.output == expected_msg

    # Check private key
    assert os.path.exists(dest_key)
    with open(dest_key, "r") as f:
        result_key = f.read()
    assert result_key.splitlines()[0] == "-----BEGIN RSA PRIVATE KEY-----"

    # Check cert
    assert not os.path.exists(dest_cert)


def test_sign_use_existing_pkey(invoker, tmp_path, mocker, fixture_dir):
    dest_cert = os.path.join(tmp_path, "dummy.crt")
    privkey_path = os.path.join(fixture_dir, "private.key")

    make_csr = mocker.patch("fasjson_client.cli.get_cert._make_csr")
    mocker.patch("fasjson_client.cli.get_cert._sign_request")
    mocker.patch("fasjson_client.cli.get_cert._write_certificate")

    result = invoker(
        "-u",
        "dummy",
        "--save-to",
        dest_cert,
        "--private-key",
        privkey_path,
        "-u",
        "dummy",
    )
    assert result.exit_code == 0
    make_csr.assert_called_once()
    call_args = make_csr.call_args[0]
    assert call_args[0] == "dummy"

    # Check that private key was actually used
    private_key = call_args[1]
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(privkey_path, "rb") as f:
        expected_key = f.read()
    assert key_pem == expected_key


def test_sign_bad_pkey(invoker, tmp_path, mocker, fixture_dir):
    dest_cert = os.path.join(tmp_path, "dummy.crt")
    privkey_path = os.path.join(tmp_path, "private.key")
    # Create the private key as an empty file
    open(privkey_path, "w").close()

    make_csr = mocker.patch("fasjson_client.cli.get_cert._make_csr")

    result = invoker(
        "-u",
        "dummy",
        "--save-to",
        dest_cert,
        "--private-key",
        privkey_path,
        "-u",
        "dummy",
    )
    assert result.exit_code == 1
    expected_msgs = (
        # cryptography < 3.3
        "Error: can't load the private key: Could not deserialize key data.\n",
        # cryptography >= 3.3, < 3.6
        "Error: can't load the private key: Could not deserialize key data."
        " The data may be in an incorrect format or it may be encrypted with"
        " an unsupported algorithm.\n",
        # cryptography >= 3.6
        "Error: can't load the private key: Could not deserialize key data."
        " The data may be in an incorrect format, it may be encrypted with"
        " an unsupported algorithm, or it may be an unsupported key type"
        " (e.g. EC curves with explicit parameters).\n",
    )
    assert any(result.output.startswith(msg) for msg in expected_msgs)
    make_csr.assert_not_called()
