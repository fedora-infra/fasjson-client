#!/usr/bin/env python3
"""
Get a certificate for the provided username.

The certificate can be an existing one or a new one. In that case a private key is either required
or generated.
"""

import logging
import os
from getpass import getuser
from textwrap import wrap

import click
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from fasjson_client import Client
from fasjson_client.config import conf
from fasjson_client.errors import ClientError, APIError


KEY_SIZE = 2048

log = logging.getLogger(__name__)


def _load_private_key(path):
    """Load a private key from the filesystem

    Args:
        path (str): path to the private key

    Returns:
        rsa.RSAPrivateKey: the private key
    """
    with open(path, "rb") as key_file:
        try:
            private_key = serialization.load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
        except ValueError as e:
            if e.args:
                e_str = "\n".join(str(arg) for arg in e.args)
            else:  # pragma: no cover
                e_str = "unknown error"
            raise click.ClickException(f"can't load the private key: {e_str}")
    return private_key


def _make_private_key(path):
    """Generate an RSA private key, store it on the filesystem and return it

    Args:
        path (str): filesystem path to store the private key

    Returns:
        rsa.RSAPrivateKey: the private key
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=KEY_SIZE, backend=default_backend()
    )
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    try:
        with open(path, "wb") as key_file:
            key_file.write(pem)
    except OSError as e:
        raise click.ClickException("can't make a private key: {}".format(e.strerror))
    return private_key


def _make_csr(username, private_key):
    """Generate a Certificate Signing Request

    Args:
        username (str): the username for this certificate
        private_key (rsa.RSAPrivateKey): the private key to sign this CSR with

    Returns:
        x509.CertificateSigningRequest: the CSR
    """
    builder = x509.CertificateSigningRequestBuilder()
    builder = builder.subject_name(
        x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, username)])
    )
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
    )
    request = builder.sign(private_key, hashes.SHA256(), default_backend())
    return request


def _load_cert_from_base64(data):
    """Load a certificate from its base64 encoding

    Args:
        data (str): a base64 representation of the certificate

    Returns:
        x509.Certificate: the certificate
    """
    pem = wrap(data, 64)
    pem.insert(0, "-----BEGIN CERTIFICATE-----")
    pem.append("-----END CERTIFICATE-----")
    pem = "\n".join(pem).encode("ascii")
    return x509.load_pem_x509_certificate(pem, default_backend())


def _sign_request(csr, username, url):
    """Sign a CSR by sending it to FASJSON

    Args:
        csr (x509.CertficateSigningRequest): the CSR
        username (str): the username that the certificate will belong to
        url (str): the URL to the FASJSON instance

    Returns:
        x509.Certificate: the signed certificate
    """
    client = Client(url)
    csr_text = csr.public_bytes(encoding=serialization.Encoding.PEM).decode("ascii")
    try:
        response = client.sign_csr(user=username, csr=csr_text)
    except APIError as e:
        raise click.ClickException(
            "could not sign the CSR ({}: {}, {}).".format(e.code, e, e.data["body"])
        )
    return _load_cert_from_base64(response.result["certificate"])


def _get_existing(username, url):
    """Get an existing certificate from FASJSON

    If multiple certificates are found, the one that will last the longest will be returned.

    Args:
        username (str): the username to get the certificate for
        url (str): the URL to the FASJSON instance

    Returns:
        x509.Certificate: the existing certificate
    """
    try:
        client = Client(url)
    except ClientError as e:
        raise click.ClickException("could not get existing certificate ({}).".format(e))

    try:
        response = client.get_user(username=username)
    except APIError as e:
        if e.code == 404:
            raise click.ClickException("user {} not found.".format(username))
        else:
            raise click.ClickException(str(e))

    certificates = response.result["certificates"]
    if not certificates:
        return None
    certificates = [_load_cert_from_base64(cert) for cert in certificates]
    # Get the latest certificate. Don't sort by serial_number, IPA may switch to randomized serial
    # numbers in the future to avoid the MD5 collision attack.
    certificates.sort(key=lambda c: c.not_valid_after)
    return certificates[-1]


def _write_certificate(cert, path):
    """Write the certificate to the filesystem in PEM format

    Args:
        cert (x509.Certificate): the certificate to write
        path (str): the filesystem path to write to
    """
    cert = cert.public_bytes(encoding=serialization.Encoding.PEM)
    with open(path, "wb") as f:
        f.write(cert)


@click.option(
    "-u", "--username", default=None, show_default=True, help="Your FAS username.",
)
@click.option(
    "-p",
    "--private-key",
    type=click.Path(),
    help="The path to the private key. If it does not exist, it will be generated.",
)
@click.option(
    "-s", "--save-to", type=click.Path(), help="The path to save your certificate to.",
)
@click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite the destination file if it exists.",
)
@click.option(
    "--existing",
    is_flag=True,
    default=False,
    help="Retrieve an existing certificate instead of generating a new one.",
)
@click.pass_context
def get_cert(ctx, username, private_key, save_to, overwrite, existing):
    """Get a certificate for the provided username.

    The certificate can be an existing one or a new one. In this case a private key is either
    required or generated.
    """

    # Fallback to config file values
    username = username or conf["get-cert"]["username"]
    private_key = private_key or conf["get-cert"]["private_key"]
    save_to = save_to or conf["get-cert"]["save_to"]
    overwrite = overwrite or conf["get-cert"]["overwrite"]
    existing = existing or conf["get-cert"]["existing"]

    # Validate options
    if save_to is None:
        raise click.BadParameter(
            "the destination file must be specified on the command line or in the "
            "configuration file. Aborting.",
            param_hint="save_to",
        )
    save_to = os.path.expanduser(save_to)
    if os.path.exists(save_to) and not overwrite:
        raise click.BadParameter(
            "the destination file {} already exists. Aborting.".format(save_to),
            param_hint="save_to",
        )
    if username is None:
        try:
            username = getuser()
        except Exception:
            raise click.BadParameter(
                "you must provide a username.", param_hint="username"
            )

    url = ctx.obj["url"]

    if existing:
        log.debug("Looking for an existing certificate...")
        cert = _get_existing(username, url)
        if cert is None:
            raise click.ClickException(
                "No existing certificate, you need to request one."
            )
        _write_certificate(cert, save_to)
        log.info("Certificate written to {}".format(save_to))
        return

    if not private_key:
        raise click.UsageError(
            "if you want a new certificate, you need to provide a path for the private key "
            "to be loaded from or saved to."
        )

    private_key = os.path.expanduser(private_key)
    if os.path.exists(private_key):
        private_key = _load_private_key(private_key)
    else:
        log.debug("Generating private key...")
        private_key = _make_private_key(private_key)

    log.debug("Generating CSR...")
    csr = _make_csr(username, private_key)

    log.debug("Uploading CSR for signature...")
    cert = _sign_request(csr, username, url)

    _write_certificate(cert, save_to)
    log.info("Certificate generated, signed and written to {}".format(save_to))
