.. _usage-label:

Usage
-----


Instantiate the client with the FASJSON URL you want to use::

   >>> from fasjson_client import Client
   >>> c = Client('http://fasjson.example.com')
   >>> c.whoami().result
   {'dn': 'uid=admin,cn=users,cn=accounts,dc=example,dc=test', 'username': 'admin', 'service': None, 'uri': 'http://fasjson.example.test/fasjson/v1/users/admin/'}


Authentication
--------------

Authentication is done with Kerberos. If you want to explicitely specify
a principal to authenticate as, use the ``principal`` constructor
argument::

   c = Client('http://fasjson.example.com', principal='admin@EXAMPLE.TEST')


Configuring an application for Kerberos authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Users authenticate via ``kinit``, applications authenticate via keytabs.
It is highly recommended to use `gssproxy <https://github.com/gssapi/gssproxy/>`_
in order to keep your keytabs secure.

-  First, install gssproxy with ``dnf install gssproxy``
-  Create the service that you want to authenticate as in IPA:
   ``ipa service-add SERVICE/host-fqdn`` (for example
   ``ipa service-add HTTP/server.example.com``)
-  Get the keytab for that service and store it in gssproxy's directory:
   ``ipa-getkeytab -p SERVICE/host-fqdn -k /var/lib/gssproxy/service.keytab``
   (for example
   ``ipa-getkeytab -p HTTP/server.example.com -k /var/lib/gssproxy/httpd.keytab``)
-  Add a configuration file for your service in gssproxy's configuration
   directory::

    # /etc/gssproxy/50-servicename.conf

    [service/servicename]
      mechs = krb5
      cred_store = keytab:/var/lib/gssproxy/service.keytab
      cred_store = client_keytab:/var/lib/gssproxy/service.keytab
      allow_constrained_delegation = true
      allow_client_ccache_sync = true
      cred_usage = both
      euid = user_the_service_runs_as

For example::

   # /etc/gssproxy/80-httpd.conf

   [service/httpd]
     mechs = krb5
     cred_store = keytab:/var/lib/gssproxy/httpd.keytab
     cred_store = client_keytab:/var/lib/gssproxy/httpd.keytab
     allow_constrained_delegation = true
     allow_client_ccache_sync = true
     cred_usage = both
     euid = apache

-  Restart gssproxy with ``systemctl restart gssproxy``
-  Configure the service to run with the ``GSS_USE_PROXY`` environment
   variable set. Services started by systemd can be configured with a
   service configuration file, for example with the httpd service::

    # /etc/systemd/system/httpd.service.d/gssproxy.conf
    # /usr/lib/systemd/system/httpd.service.d/gssproxy.conf

    [Service]
    Environment=KRB5CCNAME=/tmp/krb5cc-httpd
    Environment=GSS_USE_PROXY=yes

Your service should now be able to authenticate with Kerberos


.. _pagination-label:

Pagination
----------

Some operations can be paginated::

   >>> from fasjson_client import Client
   >>> c = Client('http://fasjson.example.com')
   >>> response = c.list_users(page_size=2)
   >>> response.result
   [{'username': 'user1', [...]}, {'username': 'user2', [...]}]

The pagination data is available in the ``page`` property::

   >>> response.page
   {'total_results': 52, 'page_size': 2, 'page_number': 1, 'total_pages': 26}

Next and previous pages are available with the ``next_page()`` and ``prev_page()`` methods,
which return the same class of objects::

   >>> response.next_page().result
   [{'username': 'user3', [...]}, {'username': 'user4', [...]}]


.. _fields-label:

Selecting attributes
--------------------

You can select which attributes you want to get from the server using the
``X-Fields`` header. The header is given as a list of attribute names::

   >>> from fasjson_client import Client
   >>> c = Client('http://fasjson.example.com')
   >>> response = c.list_users(
   ...     page_size=1,
   ...     _request_options={
   ...         "headers": {"X-Fields": ["username", "emails"]}
   ...     }
   ... )
   >>> response.result
   [{'username': 'user1', 'emails': ['user1@example.com']}]


Command line
------------

This package also provides a command-line client to do some operations.
Install the dependencies with ``poetry install -E cli`` and run ``fasjson-client --help``
to see which operations are available.
