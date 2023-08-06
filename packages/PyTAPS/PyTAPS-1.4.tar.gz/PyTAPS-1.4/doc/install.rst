===================
 Installing PyTAPS
===================

Requirements
============

In order to build PyTAPS, several external libraries are required:

* Python 2.5+
* `NumPy <http://numpy.scipy.org/>`_ 1.3.0+
* At least one of...

  * `MOAB <http://trac.mcs.anl.gov/projects/ITAPS/wiki/MOAB>`_ (or other iMesh
    interface)
  * `CGM <http://trac.mcs.anl.gov/projects/ITAPS/wiki/CGM>`_ (or other iGeom
    interface)
  * `Lasso <http://trac.mcs.anl.gov/projects/ITAPS/wiki/Lasso>`_ (or other iRel
    interface)

To run the performance tests or tools, `Matplotlib
<http://matplotlib.sourceforge.net/>`_ is also required. Finally, to build the
documentation (you're reading it!), `Sphinx <http://sphinx.pocoo.org/>`_ is
required.

With MOAB/CGM
-------------

Since Python modules are loaded as shared libraries, MOAB's iMesh library and
CGM's iGeom library should either be configured as shared libraries
(``--enable-shared``) or with position-independent code (``--with-pic``). This
obviously applies to any other iMesh/iGeom implementation, though the
configuration options may vary.

The Easy Way
============

Once you have the prerequisites, the easiest way to install PyTAPS is to use
`Pip <http://pypi.python.org/pypi/pip>`_ (0.7+ recommended)::

    pip install pytaps

This will download, compile, and install PyTAPS automatically. If you have some
but not all of the ITAPS interfaces (e.g. only iMesh), this will only install
interfaces for the libraries you have, as described in `Autodetection of
Libraries`_.

Building Manually
=================

Like many Python packages, PyTAPS uses Setuptools for installation, so in
general setup consists simply of downloading the tarball, extracting it, and
typing ``python setup.py install`` inside the extracted directory. However,
certain ITAPS interfaces may require some additional setup.

Autodetection of Libraries
--------------------------

The PyTAPS setup script supports importing definitions from the
`iXxx-Defs.inc` files, where `iXxx` is the name of the interface. PyTAPS will
attempt to find these files automatically, by searching in some common
locations:

#. The files specified in the environment variables ``IXXX_DEFS``
#. For each directory `dir` in the environment variables ``PATH`` and
   ``CPATH``, look in `dir/../lib`
#. Each directory in the environment variable ``LD_LIBRARY_PATH``
#. `/usr/local/lib`
#. `/usr/lib`

If the PyTAPS setup script cannot find the `iXxx-Defs.inc` file, it will
assume you do not have that interface installed and automatically disable it in
PyTAPS.

If you have the `iXxx-Defs.inc` files installed but not in any of the above
locations, you can specify where they are in the global command-line options
``--iXxx-path=PATH``, like so::

  python setup.py --iMesh-path=PATH install

For example, if your `iMesh-Defs.inc` is located at
`/usr/local/iMesh/lib/iMesh-Defs.inc`, then ``--iMesh-path`` should be
`/usr/local/iMesh/`. You may also specify this as `/usr/local/iMesh/lib` or
`/usr/local/iMesh/lib/iMesh-Defs.inc`. Finally, this option may be specified in
the `setup.cfg` file:

.. literalinclude:: ../setup.cfg.example
   :language: ini

If the `iMesh-Defs.inc` file was not installed, or you don't wish to use it,
you can manually specify the build options as described below.

Manually Specifying Library Locations
-------------------------------------

In some cases, required objects for building PyTAPS aren't in the expected
directories. One solution to this is to include the appropriate directories in
the environment variables ``CPATH`` and ``PYTHONPATH``. Another, more flexible
method is to use the `setup.cfg` file. Information on how to use this file can
be found in the official Python `documentation
<http://docs.python.org/install/index.html#distutils-configuration-files>`_.

Disabling Interfaces
--------------------

If you only want to build PyTAPS with a subset of the interfaces you have installed (e.g. some of them are built as static libs), you can disable the ones you don't want with the global options ``--without-iXxx``. For example, if you wanted to disable iMesh, you would run::

    python setup.py --without-iMesh install

Running Tests
=============

To run unit/regression tests on the package, you may specify ``test`` as an
argument to `setup.py` like so (after installing the package)::

    python setup.py test

If you only have some of the interfaces installed, this command will only run
tests for those interfaces. If you'd like to run a specific subset of tests (or
force all tests to be run), you can specify a test suite (or comma-separated
list of suites) to run::

    python setup.py test --test-suites=test.imesh

Performance Testing
-------------------

To run performance tests on the package comparing the speed of a pure-C
usage of ITAPS with PyTAPS, you may pass ``perf`` as a command to `setup.py`.
The performance test requires an input file to test. You may also specify the
number of times to repeat the tests::

    python setup.py perf --file=/path/to/file --count=N

The performance tests consist of two sub-commands, described below.

Building the Performance Test
_____________________________

This command builds the C portion of the performance tests. The following
options are allowed:

+--------------------------+--------+---------------------------------------+
| ``--include-dirs=PATHS`` | ``-I`` | list of directories to search for     |
|                          |        | include files                         |
+--------------------------+--------+---------------------------------------+
| ``--library-dirs=PATHS`` | ``-L`` | list of directories to search for     |
|                          |        | library files                         |
+--------------------------+--------+---------------------------------------+
| ``--libraries=LIBS``     | ``-l`` | list of libraries to link to          |
+--------------------------+--------+---------------------------------------+

Running the Performance Test
____________________________

This command executes the performance tests. The following options are allowed
(as with ``perf``):

+-----------------+--------+-------------------------------------------+
| ``--file=PATH`` | ``-F`` | file or directory containing test file(s) |
+-----------------+--------+-------------------------------------------+
| ``--count=N``   | ``-c`` | number of times to repeat each test       |
+-----------------+--------+-------------------------------------------+

Building Documentation
======================

The documentation that you're currently reading can be built from `setup.py` by
specifying ``doc`` as an argument. This command supports the following options:

+-----------------------+--------+---------------------------------------+
| ``--builder=BUILDER`` | ``-b`` | documentation builder (default: html) |
+-----------------------+--------+---------------------------------------+
| ``--target=TARGET``   | ``-t`` | target directory for output           |
+-----------------------+--------+---------------------------------------+
