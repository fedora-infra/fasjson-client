============
Contributing
============

Development
-----------

Install dependencies::

   poetry install

Run the tests::

   tox

License
-------

Licensed under `lgpl-3.0`_

.. _lgpl-3.0: https://opensource.org/licenses/lgpl-3.0.html


Release Notes
-------------

To add entries to the release notes, create a file in the ``news`` directory in the
``source.type`` name format, where the ``source`` part of the filename is:

* ``42`` when the change is described in issue ``42``
* ``PR42`` when the change has been implemented in pull request ``42``, and
  there is no associated issue
* ``Cabcdef`` when the change has been implemented in changeset ``abcdef``, and
  there is no associated issue or pull request.

And where the extension ``type`` is one of:

* ``bic``: for backwards incompatible changes
* ``dependency``: for dependency changes
* ``feature``: for new features
* ``bug``: for bug fixes
* ``dev``: for development improvements
* ``docs``: for documentation improvements
* ``other``: for other changes

The content of the file will end up in the release notes. It should not end with a ``.``
(full stop).

If it is not present already, add a file in the ``news`` directory named ``username.author``
where ``username`` is the first part of your commit's email address, and containing the name
you want to be credited as. There is a script to generate a list of authors that we run
before releasing, but creating the file manually allows you to set a custom name.

A preview of the release notes can be generated with
``towncrier --draft``.

Release Process
^^^^^^^^^^^^^^^

#. Update the version in ``pyproject.toml`` by running ``poetry version major|minor|patch``
   depending on the contents of the release.
#. Run ``poetry install`` to update the package's metadata.
#. Add missing authors to the release notes fragments by changing to the ``news`` directory and
   running the ``get-authors.py`` script, but check for duplicates and errors
#. Generate the release notes by running ``poetry run towncrier build`` (in the base directory)
#. Adjust the release notes in ``docs/release_notes.md``.
#. Generate the docs with ``tox -r -e docs`` and check them in ``docs/_build/html``.
#. Commit the changes
#. Create the release and tag in the Github webui

