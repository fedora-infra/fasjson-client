from .client import Client  # noqa: F401

# Set the version
try:
    import importlib.metadata

    __version__ = importlib.metadata.version("fasjson_client")
except ImportError:
    try:
        import pkg_resources

        try:
            __version__ = pkg_resources.get_distribution("fasjson_client").version
        except pkg_resources.DistributionNotFound:
            __version__ = None
    except ImportError:
        __version__ = None
