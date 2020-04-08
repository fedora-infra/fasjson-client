import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))


def content(path, cwd=None):
    if cwd:
        fpath = os.path.join(cwd, path)
    else:
        fpath = path
    with open(fpath) as fd:
        return fd.read()


def parse_requirements(data):
    return [l for l in data.split('\n') if l and not l.startswith('#')]


setup(
    name="fasjson-client",
    author="Fedora Infrastructure Team",
    version="0.0.1",
    author_email="infrastructure@lists.fedoraproject.org",
    description="Fedora Account System OpenAPI client",
    long_description=content("README.md", cwd=here),
    url="https://github.com/fedora-infra/fasjson-client",
    packages=find_packages(exclude=("test,")),
    include_package_data=True,
    # Possible options are at https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license="LGPLv3",
    install_requires=parse_requirements(content('requirements.txt')),
    tests_requires=parse_requirements(content('test_requirements.txt')),
    python_requires=">=3.6",
)
