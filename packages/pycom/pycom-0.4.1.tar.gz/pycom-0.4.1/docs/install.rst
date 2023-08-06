Installation
=============

You can download PyCOM from our PyPI page: http://pypi.python.org/pypi/pycom

We suggest using `pip` for PyCOM installation from source code as
`easy_install` has some issues with eggs and configuration files::

    $ pip install pycom

You can also checkout the latest code from BitBucket::

    $ hg clone https://bitbucket.org/divius/pycom

Our requirements are:

- POSIX-compatible OS (other may work)
- `Python <http://www.python.org>`_ 2.6, 2.7 or >= 3.2
- `0MQ Python bindings <http://www.zeromq.org/bindings:python>`_ >= 2.1.11
- `six <http://packages.python.org/six/>`_ for Python 3 compatibility
  (maybe we'll drop it later)

To run test suite you'll also need:

- `coverage.py <http://nedbatchelder.com/code/coverage/>`_
- `unittest2 <http://pypi.python.org/pypi/unittest2>`_ (Python 2.6 only)

Installing PyCOM is as simple as it can be::

    $ ./setup.py install

You may want to run test suite before installing::

    $ ./test.py

And finally to generate your own copy of this documentation, you'll need
`sphinx <http://sphinx.pocoo.org/>`_ utility.
Once you have all the requirements, run::

    $ cd docs
    $ make html

To start nameserver use script::

    $ /usr/local/bin/pycom-nameserver

You may need to adjust nameserver configuration
(see :doc:`config` for details).
