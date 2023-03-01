# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

topdir = os.path.abspath("../")
sys.path.insert(0, topdir)

# Set the full version, including alpha/beta/rc tags
try:
    import fasjson_client  # NOQA

    release = fasjson_client.__version__
except ImportError:
    import toml

    pyproject = toml.load(os.path.join(topdir, "pyproject.toml"))
    release = pyproject["tool"]["poetry"]["version"]


# -- Project information -----------------------------------------------------

project = "fasjson-client"
copyright = "2020, Red Hat, Inc"
author = "Fedora Infrastructure"

# The short X.Y version
version = ".".join(release.split(".")[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Explcitely set the master doc
# https://github.com/readthedocs/readthedocs.org/issues/2569
master_doc = "index"


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"


# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "github_user": "fedora-infra",
    "github_repo": "fasjson-client",
    "page_width": "1040px",
    "show_related": True,
    "sidebar_collapse": True,
    "caption_font_size": "140%",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- Extension configuration -------------------------------------------------

autodoc_mock_imports = ["gssapi", "requests_gssapi"]

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

extlinks = {
    "commit": ("https://github.com/fedora-infra/fasjson-client/commit/%s", "%s"),
    "issue": ("https://github.com/fedora-infra/fasjson-client/issues/%s", "#%s"),
    "pr": ("https://github.com/fedora-infra/fasjson-client/pull/%s", "PR#%s"),
}
