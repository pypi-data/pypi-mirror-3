Funkload base test cases for Openerp
====================================

Introduction
~~~~~~~~~~~~
This package provides the ``OpenERPTestCase`` class, subclassing
``FunkloadTestCase`` with methods tailored for OpenERP functionnal and
load testing through the XML-RPC API.

It features login and user management facilities, and pythonic
encapsulation of XML-RPC calls through the ModelProxy class.

For a detailed example, see the included ``test_sales_order.py`` test
case.

Basic user handling
~~~~~~~~~~~~~~~~~~~

Funkload can create if needed users with given groups and login as
them. Note how groups are specified as fully qualified references from
``ir.model.data``::

  from anybox.funkload.openerp import OpenERPTestCase

  class MyTestCase(OpenERPTestCase):

      def test_01_makeuser(self):
          self.login('admin', 'admin')
          self.ensure_user('spam', 'spampassword', ['base.group_sale_manager'])

      def test_02_my_usecase(self):
          self.login('spam', 'spampassword')
          ...

It is a common practice to use a test case to prepare the
database. ``fl-run-test`` loads them in alphabetical order.

User handling through Funkload's credential server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Funkload provides an external and optional credentials server. This is
a facility that you are in no way forced to use.

The principle is to serve logins, passwords, and groups, loaded from separate
external ``users.txt`` and ``groups.txt`` files. Groups in that sense
are thought as groups of users, which is a slightly different
philosophy as OpenERP's but it doesn't matter much.

OpenERPTestCase provides a login method that selects an user from the
wished group from the credential server::

    def test_my_usecase(self):
        self.login_as_group('base.group_sale_manager')
        # now test some scenario

Of course that means that the names of groups must also be consistent
in ``groups.txt.``. See the provided ``users.txt`` and ``groups.txt``
files.

There is also a method ``ensure_credential_server_users()`` that
creates all wished users with the appropriate groups.

API calls
~~~~~~~~~
The principle is to get a ``ModelProxy`` instance, that'll encapsulate
all regular (so-called ORM) calls::

    def test_my_usecase(self):
        """First list all customers, then..."""
        self.login('user', 'password')
        res_partner = self.model('res.partner')
        res_partner.model.search([('customer', '=', 'True')],
                                 description="Search customers")

The description will end up as request title in the Funkload bench report

Workflow calls
~~~~~~~~~~~~~~

The ``ModelProxy`` instances provided by the ``model()`` method can
also perform workflow's trigger validate::

     def test_my_usecase(self):
         # some preparations, then confirm Sale Order #1234
         model = self.model('sale.order')
         model.workflow('order_confirm')(1234,
                                         description="Confirm Sale Order")

As before, the description if for the bench report.

References
~~~~~~~~~~

The ``OpenERPTestCase`` class has the ``ref()`` method, to retrieve an
object id from the reference code, as in XML or YML files, namely from
``ir.model.data``::

    def test_my_usecase(self):
        product_id = self.ref('product.product', 'stock', 

Acknowledgment
~~~~~~~~~~~~~~
The very simple wrapping provided by ``ModelProxy`` is inspired by the
OpenObject library.

Tips for benchmarking
~~~~~~~~~~~~~~~~~~~~~

Randomize as much as you can. Notably, you *must avoid* repeated
logins with the same user : this spawns database conflicts, putting
some test runs in error state, but also making them very fast, hence
making you stats unusable.

Anything that's in ``setUp()`` is outside of performance
measurements. See how the provided ``test_sales_orders`` preloads
available customers and sellable products once for all for each
virtual user.

.. Emacs
.. Local Variables:
.. mode: rst
.. End:
.. Vim
.. vim: set filetype=rst:









