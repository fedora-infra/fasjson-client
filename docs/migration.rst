Migrating from python-fedora
----------------------------

Fasjson-client provides functionality for the most important endpoints previously exposed in python-fedora.
Below is a list of common python-fedora endpoints and their fasjson-client alternatives.


Creating a client
******************

The instantiation of a client can be done similarly to python-fedora, except there is no need to provide a username and password with which to authenticate. Instead, this authentication is performed by your service via Kerberos.

For more information, please see :ref:`usage-label`. The content below assumes you have setup your client as detailed in :ref:`usage-label`.

Pagination is supported in some of the ``fasjson_client`` API calls listed below, for more information about how to use it see :ref:`pagination-label`.

The following sections are divided by the objects requested, and each corresponding python-fedora method is listed as a heading - with the appropriate fasjson-client endpoint then explained below.

Groups
******

group_by_id
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You must now use the ``groupname`` instead of ``id``.

    >>> client.get_group(groupname="testGroup").result
    {'groupname': 'testGroup', 'uri': 'http://fasjson.example.test/fasjson/v1/groups/testGroup/'}

group_by_name
~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> client.get_group(groupname="testGroup").result
    {'groupname': 'testGroup', 'uri': 'http://fasjson.example.test/fasjson/v1/groups/testGroup/'}

group_members
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    >>> client.get_group_members(groupname="testGroup", page_size=5).result
    [{'username': 'user1', [...]}, {'username': 'user2', [...]}]

People
******

person_by_id
~~~~~~~~~~~~~~~~~~~~~~~~

You must now use the person's ``username`` instead of ``id``

    >>> client.get_user(username="test").result
    {'username': 'test', 'surname': 'user', 'givenname': 'test', 'emails': ['test@example.test'], 'ircnicks': ['test', 'test_1'], 'locale': 'en-US', 'timezone': None, 'gpgkeyids': None, 'certificates': None, 'creation': None, 'locked': False, 'uri': 'http://fasjson.example.test/fasjson/v1/users/test/'}


person_by_username
~~~~~~~~~~~~~~~~~~

    >>> client.get_user(username="test").result
    {'username': 'test', 'surname': 'user', 'givenname': 'test', 'emails': ['test@example.test'], 'ircnicks': ['test', 'test_1'], 'locale': 'en-US', 'timezone': None, 'gpgkeyids': None, 'certificates': None, 'creation': None, 'locked': False, 'uri': 'http://fasjson.example.test/fasjson/v1/users/test/'}


user_data
~~~~~~~~~~~~~~

    >>> client.list_users(page_size=50).result
    [{'username': 'user1', [...]}, {'username': 'user2', [...]}]


people_by_groupname
~~~~~~~~~~~~~~~~~~~

    >>> client.get_group_members(groupname="testGroup", page_size=5).result
    [{'username': 'user1', [...]}, {'username': 'user2', [...]}]


Getting all items at once
*************************

The ``list_all_entities`` method is an iterator over all records of an entity in FASJSON, for
example ``users`` or ``groups``. They will be retrieved in multiple server calls (using pagination).
You can specify the number of users that should be returned in each server call in the ``page_size``
argument if you have performance issues, but the default should be fine. An example with users::

    >>> for user in client.list_all_entities("users", page_size=1000):
    ...     print(user)
    {'username': 'user1', [...]}
    {'username': 'user2', [...]}
    {'username': 'user3', [...]}
    [...]
