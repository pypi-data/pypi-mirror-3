.. _download-install:

Download and install instructions
=================================

Python Package Index (PyPI)
---------------------------

You can install OERPLib with the `easy_install` tool::

    $ easy_install oerplib

Or with `pip`::

    $ pip install oerplib

An alternative way is to download the tarball from
`Python Package Index <http://pypi.python.org/pypi/OERPLib/>`_ page,
and install manually (replace `X.Y.Z` accordingly)::

    $ wget http://pypi.python.org/packages/source/O/OERPLib/OERPLib-X.Y.Z.tar.gz
    $ tar xzvf OERPLib-X.Y.Z.tar.gz
    $ cd OERPLib-X.Y.Z
    $ python setup.py install

No dependency is required.

Source code
-----------

The project is hosted on `Launchpad <https://launchpad.net/oerplib>`_.
To get the current development branch, just type::

    $ bzr branch lp:oerplib

For the last version of a stable branch (replace `X.Y` accordingly)::

    $ bzr branch lp:oerplib/X.Y

Run tests
---------

.. versionadded:: 0.4.0

To run unit tests from the project directory, run the following command::

    PYTHONPATH=. ./tests/runtests.py --help

Then, set your parameters in order to indicate the `OpenERP` server on which
you want to perform the tests, for instance::

    PYTHONPATH=. ./tests/runtests.py --create_db --server 192.168.1.4

The name of the database created is 'oerplib-test' by default.

