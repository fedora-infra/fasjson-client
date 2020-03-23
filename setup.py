# coding: utf-8

from setuptools import setup, find_packages  # noqa: H301


setup(
    name='fasjsonclient',
    version='0.0.1',
    description='Fedora Account Service JSON API Client',
    author='Fedora Inrastucture team',
    author_email='team@openapitools.org',
    url='https://github.com/fedora-infra/fasjson-client',
    keywords=['OpenAPI', 'Fedora Account Service JSON API', 'fas'],
    install_requires=[
        'urllib3 >= 1.25.8',
        'six >= 1.14.0',
        'certifi==2019.11.28',
        'python-dateutil==2.8.1',
        'gssapi==1.6.2',
        'requests==2.23.0',
        'requests-gssapi==1.2.0',
    ],
    packages=find_packages(exclude=['test', 'tests']),
    include_package_data=True,
    license="GPLv3",
    long_description='''
    fajson rest api
    '''
)
